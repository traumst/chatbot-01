"""FastApi router for our application"""

import logging
from logging import Logger

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from src.api.route import home, ask, convo, history, favicon
from src.utils.lru_cache import LRUCache

templates = Jinja2Templates(directory="src/template")

logger: Logger = logging.getLogger(__name__)

def init_api(query_cache: LRUCache) -> FastAPI:
    """Creates new instance of FastAPI with included router"""

    app = FastAPI(title="LLM Query API", version="1.0")
    # pylint: disable=no-member
    app.state.query_cache = query_cache
    app.include_router(home.router)
    app.include_router(ask.router)
    app.include_router(convo.router)
    app.include_router(history.router)
    app.include_router(favicon.router)
    # api/middleware/todo.py
    return app
