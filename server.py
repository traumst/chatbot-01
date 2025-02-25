"""Web server exposing cached queries"""

import logging

import uvicorn
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

import src.db.database as db
import src.utils.logmod
from src.api.router import init_api
from src.utils.env_config import read_env, EnvConfig
from src.utils.lru_cache import LRUCache

runtime_config: EnvConfig = read_env()
templates = Jinja2Templates(directory="src/template")
query_cache = LRUCache(size=runtime_config.cache_size)
src.utils.logmod.init(runtime_config.log_level)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting server")
    db.run_migrations()
    app: FastAPI = init_api()
    uvicorn.run(
        "server:app",
        host=runtime_config.host,
        port=runtime_config.port,
        proxy_headers=True,
        reload=True,
    )
