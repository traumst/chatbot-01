"""Web server exposing cached queries"""

import datetime
import logging
import os
from typing import List, Optional

import uvicorn
from alembic.config import Config
from fastapi import FastAPI, Request, Depends, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from rich.logging import RichHandler
from sqlalchemy.orm import Session
from alembic import command

import src.middleware.db_session as db_middleware
import src.middleware.validate_query as query_middleware
import src.db.query_log as query_log
from src.db.query_log import QueryLog
from src.schemas.query_request import QueryRequest
from src.utils.env_config import read_env, EnvConfig
from src.utils.lru_cache import LRUCache

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(asctime)s @%(name)s: %(message)s",
    datefmt="[%Y-%m-%dT%H:%M:%S]",
    handlers=[
        RichHandler(show_time=False, show_level=False, show_path=False)
        # logging.FileHandler(f"general.log"),
        # logging.StreamHandler(sys.stdout),
    ])
logger.warning("Logging enabled with level %s", logger.level)

runtime_config: EnvConfig = read_env()
templates = Jinja2Templates(directory="src/template")
query_cache: LRUCache = LRUCache(size=runtime_config.cache_size)

router = APIRouter()

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
    query_response: Optional[QueryLog] = query_cache.get(user_query)
    if query_response is not None:
        logger.info(f"Cached response is being served: {query_data.query}: {query_response.response_text}")
        return templates.TemplateResponse("log_entry.html", {"request": request, "entry": query_response})

    # still, maybe we already answered this query previously
    query_hash = user_query.__hash__()
    stored_response: QueryLog | None = query_log.get_query_log(db, query_hash)
    if stored_response is not None and stored_response.query_text == user_query:
        logger.info(f"Caching and serving stored response: {user_query}: {stored_response.response_text}")
        query_cache.put(user_query, stored_response)
        stored_response.updated_at = datetime.datetime.now()
        query_log.update_query_record(db, stored_response)
        # todo
        return templates.TemplateResponse("log_entry.html", {"request": request, "entry": stored_response})

    # produce new response,
    logger.info(f"New query will be stored and cached: {user_query}")
    inverted_text: str = query_data.query[::-1]

    # store it for reuse
    query_response = query_log.create_query_log(db, query_data.query, response_text=inverted_text)
    if query_response is None:
        # TODO create info message, explain what failed
        raise RuntimeError("failed to persist query for later")

    query_cache.put(user_query, query_response)
    return templates.TemplateResponse("log_entry.html", {"request": request, "entry": query_response})

@router.get("/home", response_class=HTMLResponse)
async def read_home(request: Request, db: Session = Depends(db_middleware.get_db)):
    """Home page, displaying past queries"""
    logger.info(f"Serving home to {request.client}")
    logs: List[QueryLog] = query_log.get_query_logs(db, offset=0, limit=10)

    return templates.TemplateResponse("home.html", {"request": request, "logs": logs})


# @router.get("/log", response_model=list[QueryLog])
# async def read_log(
#     request: Request,
#     query_id: Optional[int] = Query(None),
#     from_offset: Optional[int] = Query(0, alias="from"),
#     db: Session = Depends(get_db)
# ) -> List[QueryLog]:
#     """Get one or more queries from the log"""
#     logger.info(f"Serving query log for {request.client}: query-{query_id}, offset-{from_offset}")
#     logs: List[QueryLog]
#     if query_id is not None:
#         logs = [query_log.get_query_log(db, query_id=query_id)]
#         if len(logs) == 0:
#             raise HTTPException(status_code=404, detail="Query not found")
#     elif from_offset is not None:
#         logs = query_log.get_query_logs(db, skip=from_offset)
#     else:
#         logs = query_log.get_query_logs(db, skip=0, limit=10)
#
#     return logs

app = FastAPI(title="LLM Query API", version="1.0")
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
#
# @asynccontextmanager
# async def lifespan(_: FastAPI):
#     logger.info("Starting up...")
#     alembic_cfg = Config("alembic.ini")
#     logger.info("run alembic upgrade head...")
#     command.upgrade(alembic_cfg, "head")
#     yield
#     logger.info("Shutting down...")



# def check_migration_state(expected_revision: Optional[str]) -> bool:
#     if expected_revision is None:
#         return False
#     with engine.connect() as conn:
#         result = conn.execute(text("SELECT version_num FROM alembic_version"))
#         current_revision = result.scalar()
#         return current_revision == expected_revision

def run_migrations():
    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), "alembic.ini"))
    command.upgrade(alembic_cfg, "head")

# Run the server if  ran directly
if __name__ == "__main__":

    # if not check_migration_state():
    run_migrations()
    uvicorn.run(
        "server:app",
        host=runtime_config.host,
        port=runtime_config.port,
        proxy_headers=True,
        reload=True)
