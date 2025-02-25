"""
Serves home page to the user, presenting input for new query,
    and a history of previous messages.
"""

import logging
from logging import Logger
from typing import List

from fastapi import Request, Depends, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import src.api.middleware.db_session as db_middleware
from src.db import generation_record

templates = Jinja2Templates(directory="src/template")

logger: Logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def home(
        request: Request,
        db_session: Session = Depends(db_middleware.get_db_session),
) -> HTMLResponse:
    """Home page, displaying past queries"""

    logger.info("Serving home to %s", request.client)
    # TODO query_cache: LRUCache = request.app.state.query_cache
    logs: List[generation_record.GenerationRecord] = generation_record.get_records(
        db_session,
        offset=0,
        limit=10,
    )
    if len(logs) > 0:
        logs[0] = generation_record.get_record(db_session, logs[0].id)
        logs[0].clickable = False

    return templates.TemplateResponse("home.html", {"request": request, "logs": logs})
