"""Web server exposing cached queries"""

import datetime
import logging
import os
from logging import Logger
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, Request, Depends, APIRouter, Query, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.schemas.gen_req import GenerationRequest
import src.api.generate as llm_api_generate
import src.api.middleware.db_session as db_middleware
import src.api.middleware.validate_query as query_middleware
import src.db.database as db
from src.db import generation_record
import src.utils.logmod
from src.utils.env_config import read_env, EnvConfig
from src.utils.lru_cache import LRUCache

runtime_config: EnvConfig = read_env()
templates = Jinja2Templates(directory="src/template")
query_cache = LRUCache(size=runtime_config.cache_size)
src.utils.logmod.init(runtime_config.log_level)

logger: Logger = logging.getLogger(__name__)

app = FastAPI(title="LLM Query API", version="1.0")
router = APIRouter()

@router.get("/favicon.ico", response_class=FileResponse)
async def favicon() -> FileResponse:
    """favicon"""

    logger.debug("serving favicon...")
    return FileResponse(f"{os.getcwd()}/src/img/scarab-bnw.svg", media_type="image/svg+xml")

@router.get("/", response_class=HTMLResponse)
async def read_home(
        request: Request,
        db_session: Session = Depends(db_middleware.get_db),
) -> HTMLResponse:
    """Home page, displaying past queries"""

    logger.info("Serving home to %s", request.client)
    logs: List[generation_record.GenerationRecord] = generation_record.get_query_logs(
        db_session,
        offset=0,
        limit=10,
    )
    if len(logs) > 0:
        logs[0] = generation_record.get_query_log(db_session, logs[0].id)
        logs[0].clickable = False

    return templates.TemplateResponse("home.html", {"request": request, "logs": logs})

@router.post("/query", response_class=StreamingResponse)
async def generation_request(
    request: Request,
    prompt: GenerationRequest = Depends(query_middleware.validate_query),
    db_session: Session = Depends(db_middleware.get_db)
) -> HTMLResponse:
    """Makes requests to Ollama API Generate"""
    logger.info("Received query from %s: %s", request.client, prompt.query)
    user_query: str = f"{prompt.query}"
    # maybe we already cached response for this query
    query_log_record: Optional[generation_record.GenerationRecord] = query_cache.get(user_query)
    if query_log_record is not None:
        logger.debug("Serving from cache, query:'%s', response:'%s'",
                     prompt.query, query_log_record.response_text)
        query_log_record.clickable = False
        return templates.TemplateResponse(
            "log_entry.html", {
                "request": request,
                "entry": query_log_record
            })

    # still, maybe we already answered this query previously
    query_hash = hash(user_query)
    query_log_record = generation_record.get_query_log(db_session, query_hash)
    if query_log_record is not None and query_log_record.query_text == user_query:
        logger.info("Serving stored response: %s: %s", user_query, query_log_record.response_text)
        query_cache.put(user_query, query_log_record)
        query_log_record.updated_at = datetime.datetime.now()
        generation_record.update_query_record(db_session, query_log_record)
        query_log_record.clickable = False
        return templates.TemplateResponse(
            "log_entry.html",{
                "request": request,
                "entry": query_log_record,
            })

    logger.info("Making generation request: %s", )
    responses: [str] = []
    async for part in llm_api_generate.generate(prompt.query):
        # TODO send chunks as they arrive
        responses.append(part)

    # store and cache for reuse
    query_log_record = generation_record.create_query_log(
        db_session,
        prompt.query,
        response_text="".join(responses),
    )
    if query_log_record is None:
        logger.error('Failed to save new query record for "%s"', prompt.query)
        raise RuntimeError("failed to persist query for later")
    query_cache.put(user_query, query_log_record)
    query_log_record.clickable = False

    return templates.TemplateResponse(
        "log_entry.html", {
            "request": request,
            "entry": query_log_record,
        })

@router.get("/log", response_class=HTMLResponse)
async def read_log(
    request: Request,
    db_session: Session = Depends(db_middleware.get_db),
    query_id: Optional[int] = Query(0, alias="id", ge=1),
) -> HTMLResponse:
    """Get one or more queries from the log"""

    logger.info("Serving query id=%s for %s:%d", query_id, request.client.host, request.client.port)
    if query_id is None:
        raise ValueError("query_id is required")
    if isinstance(query_id, int) is False or query_id < 1:
        raise ValueError("query_id must be positive integer")
    query_log_record = generation_record.get_query_log(db_session, query_id=query_id)
    if query_log_record is None:
        raise HTTPException(
            status_code=555,
            detail="Query not found",
            headers={"Retry-After": "30"},
        )

    return templates.TemplateResponse(
        "log_entry.html", {
            "request": request,
            "entry": query_log_record,
        })

app.include_router(router)

# api/middleware/todo.py

if __name__ == "__main__":
    db.run_migrations()
    uvicorn.run(
        "server:app",
        host=runtime_config.host,
        port=runtime_config.port,
        proxy_headers=True,
        reload=True,
    )
