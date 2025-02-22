"""Web server exposing cached queries"""

import datetime
import logging
import os
from logging import Logger
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, Request, Depends, APIRouter, Query, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.db.database import run_migrations
import src.db.generation_record as query_log
import src.api.middleware.db_session as db_middleware
import src.api.middleware.validate_query as query_middleware
from src.llm.models import GenerationResponse
from src.utils.logmod import init as init_log
from src.db.generation_record import GenerationRecord
from src.schemas.generation_request import GenerationRequest
from src.utils.env_config import read_env, EnvConfig
from src.utils.lru_cache import LRUCache
from src.llm.ollama import generate

runtime_config: EnvConfig = read_env()
templates = Jinja2Templates(directory="src/template")
query_cache = LRUCache(size=runtime_config.cache_size)
init_log(runtime_config.log_level)

logger: Logger = logging.getLogger(__name__)

app = FastAPI(title="LLM Query API", version="1.0")
router = APIRouter()

@router.get("/favicon.ico", response_class=FileResponse)
async def favicon() -> FileResponse:
    logger.debug("serving favicon...")
    return FileResponse(f"{os.getcwd()}/src/img/scarab-bnw.svg", media_type="image/svg+xml")

@router.get("/", response_class=HTMLResponse)
async def read_home(request: Request, db: Session = Depends(db_middleware.get_db)) -> HTMLResponse:
    """Home page, displaying past queries"""
    logger.info(f"Serving home to {request.client}")
    logs: List[GenerationRecord] = query_log.get_query_logs(db, offset=0, limit=10)
    if len(logs) > 0:
        logs[0] = query_log.get_query_log(db, logs[0].id)
        logs[0].clickable = False

    return templates.TemplateResponse("home.html", {"request": request, "logs": logs})

@router.post("/query", response_class=HTMLResponse)
async def generation_request(
    request: Request,
    prompt: GenerationRequest = Depends(query_middleware.validate_query),
    db: Session = Depends(db_middleware.get_db)
) -> HTMLResponse:
    """Makes requests to Ollama API Generate"""
    logger.info(f"Received query from {request.client}: {prompt.query}")
    user_query: str = f"{prompt.query}"
    # maybe we already cached response for this query
    query_log_record: Optional[GenerationRecord] = query_cache.get(user_query)
    if query_log_record is not None:
        logger.info(f"Cached response is being served: {prompt.query}: {query_log_record.response_text}")
        query_log_record.clickable = False
        return templates.TemplateResponse("log_entry.html", {"request": request, "entry": query_log_record})

    # still, maybe we already answered this query previously
    query_hash = user_query.__hash__()
    query_log_record = query_log.get_query_log(db, query_hash)
    if query_log_record is not None and query_log_record.query_text == user_query:
        logger.info(f"Serving stored response: {user_query}: {query_log_record.response_text}")
        query_cache.put(user_query, query_log_record)
        query_log_record.updated_at = datetime.datetime.now()
        query_log.update_query_record(db, query_log_record)
        query_log_record.clickable = False
        return templates.TemplateResponse("log_entry.html", {"request": request, "entry": query_log_record})

    logger.info(f"Making generation request: {user_query}")
    # TODO don't wait, send chunks as they arrive
    responses: [GenerationResponse] = []
    part: GenerationResponse | ValueError | None
    async for part in generate(prompt.query):
        if part is None:
            logger.warning("error occurred while generating response for '%s'", prompt.query)
            continue
        if part is ValueError:
            logger.error("error occurred while generating response for '%s', %s", prompt.query, part)
            continue
        if hasattr(part, "response"):
            responses.append(part)
            continue
        break

    # store and cache for reuse
    response_text = "".join([res.response for res in responses])
    query_log_record = query_log.create_query_log(db, prompt.query, response_text=response_text)
    if query_log_record is None:
        logger.error(f'Failed to save new query record for "{prompt.query}"')
        raise RuntimeError("failed to persist query for later")
    query_cache.put(user_query, query_log_record)
    query_log_record.clickable = False

    return templates.TemplateResponse("log_entry.html", {"request": request, "entry": query_log_record})

@router.get("/log", response_class=HTMLResponse)
async def read_log(
    request: Request,
    db: Session = Depends(db_middleware.get_db),
    query_id: Optional[int] = Query(0, alias="id", ge=1),
) -> HTMLResponse:
    """Get one or more queries from the log"""
    logger.info(f"Serving query id={query_id} for {request.client.host}:{request.client.port}")
    if query_id is None:
        raise ValueError("query_id is required")
    if type(query_id) is not int or query_id < 1:
        raise ValueError("query_id must be positive integer")
    query_log_record = query_log.get_query_log(db, query_id=query_id)
    if query_log_record is None:
        raise HTTPException(status_code=555, detail="Query not found", headers={"Retry-After": "30"})

    return templates.TemplateResponse("log_entry.html", {"request": request, "entry": query_log_record})

app.include_router(router)

# api/middleware/todo.py

# Run the server if ran directly
if __name__ == "__main__":
    # if not check_migration_state():
    run_migrations()
    uvicorn.run(
        "server:app",
        host=runtime_config.host,
        port=runtime_config.port,
        proxy_headers=True,
        reload=True)