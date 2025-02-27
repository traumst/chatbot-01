"""Web server exposing cached queries"""

import logging

import uvicorn
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

import src.db.database as db
import src.utils.logmod
from src.api.router import init_fastapi_with_router
from src.utils.env_config import read_env, EnvConfig
from src.utils.lru_cache import LRUCache

runtime_config: EnvConfig = read_env()
templates = Jinja2Templates(directory="src/template")
src.utils.logmod.init(runtime_config.log_level)

logger = logging.getLogger(__name__)

query_cache = LRUCache(size=runtime_config.cache_size)
app: FastAPI = init_fastapi_with_router(query_cache)

if __name__ == "__main__":
    logger.info("Starting server")
    db.upgrade_db()
    uvicorn.run(
        "server:app",
        host=runtime_config.host,
        port=runtime_config.port,
        proxy_headers=True,
        reload=True,
    )
