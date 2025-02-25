"""
Chat with the model while keeping track of previous messages from each side - user and the bot.
"""

import logging
from logging import Logger

from fastapi import Request, Depends, APIRouter
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import src.api.middleware.db_session as db_middleware
import src.api.middleware.validate_query as query_middleware
import src.ollama.chat as chat
from src.db import generation_record
from src.schemas.gen_req import GenerationRequest

templates = Jinja2Templates(directory="src/template")

logger: Logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/convo", response_class=StreamingResponse)
async def convo(
    request: Request,
    prompt: GenerationRequest = Depends(query_middleware.validate_query),
    db_session: Session = Depends(db_middleware.get_db_session)
) -> HTMLResponse:
    """Back and forth messaging with history"""

    logger.info("Received CONVO request from %s: %s", request.client, prompt.query)
    # TODO query_cache: LRUCache = request.app.state.query_cache
    responses: [str] = []
    async for part in chat.model_chat(prompt.query):
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
    # TODO query_cache.put(prompt.query, query_log_record)
    query_log_record.clickable = False

    return templates.TemplateResponse(
        "log_entry.html", {
            "request": request,
            "entry": query_log_record,
        })
