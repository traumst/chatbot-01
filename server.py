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
import src.db.query_log as query_log
import src.middleware.db_session as db_middleware
import src.middleware.validate_query as query_middleware
from src.utils.logmod import init as init_log
from src.db.query_log import QueryLog
from src.schemas.query_request import QueryRequest
from src.utils.env_config import read_env, EnvConfig
from src.utils.lru_cache import LRUCache

runtime_config: EnvConfig = read_env()
templates = Jinja2Templates(directory="src/template")
query_cache = LRUCache(size=runtime_config.cache_size)
init_log(runtime_config.log_level)

logger: Logger = logging.getLogger(__name__)

app = FastAPI(title="LLM Query API", version="1.0")
router = APIRouter()

@router.get("/favicon.ico", response_class=FileResponse)
async def favicon():
    logger.debug("serving favicon...")
    return FileResponse(f"{os.getcwd()}/src/img/scarab-bnw.svg", media_type="image/svg+xml")

@router.get("/", response_class=HTMLResponse)
async def read_home(request: Request, db: Session = Depends(db_middleware.get_db)):
    """Home page, displaying past queries"""
    logger.info(f"Serving home to {request.client}")
    logs: List[QueryLog] = query_log.get_query_logs(db, offset=0, limit=10)
    if len(logs) > 0:
        for idx, log in enumerate(logs):
            if idx == 0:
                # top log item should contain whole query and response
                # and also not be clickable
                last = query_log.get_query_log(db, logs[0].id)
                last.clickable = False
                logs[idx] = last
            else:
                # log.set_clickable(True)
                pass

    return templates.TemplateResponse("home.html", {"request": request, "logs": logs})

@router.post("/query", response_class=HTMLResponse)
async def create_query(
    request: Request,
    query_data: QueryRequest = Depends(query_middleware.validate_query),
    db: Session = Depends(db_middleware.get_db)
):
    """Simulate processing by reversing the query text"""
    logger.info(f"Received query from {request.client}: {query_data.query}")
    user_query: str = f"{query_data.query}"
    # maybe we already cached response for this query
    query_log_record: Optional[QueryLog] = query_cache.get(user_query)
    if query_log_record is not None:
        logger.info(f"Cached response is being served: {query_data.query}: {query_log_record.response_text}")
        query_log_record.clickable = False
        return templates.TemplateResponse("log_entry.html", {"request": request, "entry": query_log_record})

    # still, maybe we already answered this query previously
    query_hash = user_query.__hash__()
    query_log_record = query_log.get_query_log(db, query_hash)
    if query_log_record is not None and query_log_record.query_text == user_query:
        logger.info(f"Caching and serving stored response: {user_query}: {query_log_record.response_text}")
        query_cache.put(user_query, query_log_record)
        query_log_record.updated_at = datetime.datetime.now()
        query_log.update_query_record(db, query_log_record)
        query_log_record.clickable = False
        return templates.TemplateResponse("log_entry.html", {"request": request, "entry": query_log_record})

    # produce new response,
    logger.info(f"New query will be stored and cached: {user_query}")
    inverted_text: str = query_data.query[::-1]

    # store it for reuse
    query_log_record = query_log.create_query_log(db, query_data.query, response_text=inverted_text)
    if query_log_record is None:
        # TODO create info message, explain what failed
        raise RuntimeError("failed to persist query for later")

    query_cache.put(user_query, query_log_record)
    query_log_record.clickable = False
    return templates.TemplateResponse("log_entry.html", {"request": request, "entry": query_log_record})

@router.get("/log", response_class=HTMLResponse)
async def read_log(
    request: Request,
    db: Session = Depends(db_middleware.get_db),
    query_id: Optional[int] = Query(0, alias="id", ge=1),
):
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

# @app.middleware("http")
# async def query_caching_middleware(request: Request, call_next):
#     logger.info("hello!")
#     return await call_next(request)
#
# @app.middleware("http")
# async def process_timing_middleware(request: Request, call_next):
#     t0 = datetime.datetime.now()
#     response = await call_next(request)
#     dt = (datetime.datetime.now() - t0)
#     logger.info(f"processing {request.url} took {dt}")
#     return response
#
# @asynccontextmanager
# async def lifespan(_: FastAPI):
#     logger.info("Starting up...")
#     alembic_cfg = Config("alembic.ini")
#     logger.info("run alembic upgrade head...")
#     command.upgrade(alembic_cfg, "head")
#     yield
#     logger.info("Shutting down...")
#
# def check_migration_state(expected_revision: Optional[str]) -> bool:
#     if expected_revision is None:
#         return False
#     with engine.connect() as conn:
#         result = conn.execute(text("SELECT version_num FROM alembic_version"))
#         current_revision = result.scalar()
#         return current_revision == expected_revision


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