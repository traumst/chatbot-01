"""FastApi router for our application"""

import logging
from logging import Logger

import asyncio
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from src.api.route import home, ask, chat, history, favicon
from src.utils.lru_cache import LRUCache

templates = Jinja2Templates(directory="src/template")

logger: Logger = logging.getLogger(__name__)

def init_fastapi_with_router(query_cache: LRUCache, chat_cache: LRUCache) -> FastAPI:
    """Creates new instance of FastAPI with included router"""

    app = FastAPI(title="LLM Query API", version="1.0")

    app.state.global_lock = asyncio.Lock() # type: ignore[attr-defined]
    app.state.chat_locks = {}  # type: ignore[attr-defined]

    app.state.query_cache = query_cache # type: ignore[attr-defined]
    app.state.chat_cache = chat_cache # type: ignore[attr-defined]
    app.include_router(home.router)
    app.include_router(ask.router)
    app.include_router(chat.router)
    app.include_router(history.router)
    app.include_router(favicon.router)
    # api/middleware/todo.py
    return app
