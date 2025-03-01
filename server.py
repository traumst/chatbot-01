"""Web server exposing cached queries"""

import logging

import uvicorn
from fastapi import FastAPI

import src.db.database as db
import src.utils.logmod
from src.api.router import init_fastapi_with_router
from src.utils.env_config import read_env, EnvConfig
from src.utils.lru_cache import LRUCache

runtime_config: EnvConfig = read_env()
src.utils.logmod.init(runtime_config.log_level)

logger = logging.getLogger(__name__)
query_cache = LRUCache(size=runtime_config.cache_size)
chat_cache = LRUCache(size=runtime_config.cache_size)
app: FastAPI = init_fastapi_with_router(query_cache=query_cache,chat_cache=chat_cache)

if __name__ == "__main__":
    try:
        logger.info("Starting server at %s:%s", runtime_config.host, runtime_config.port)
        db.upgrade_db()
        uvicorn.run(
            "server:app",
            host=runtime_config.host,
            port=runtime_config.port,
            proxy_headers=True,
            reload=True,
        )
    except Exception as e: # pylint: disable=broad-except
        logger.fatal(e)
