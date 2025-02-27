"""
One-off shot query to the model with all context provided in a single prompt
"""

import logging
from logging import Logger
from typing import Optional

from fastapi import Request, Depends, APIRouter, HTTPException
from fastapi import status
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import src.api.middleware.db_session as db_middleware
import src.api.middleware.validate_query as query_middleware
import src.ollama.ask as llm_api
from src.db.tables.ask_record import AskRecord, get_record, create_record, update_record
from src.schemas.ask_req import AskRequest
from src.utils.lru_cache import LRUCache

templates = Jinja2Templates(directory="src/template")

logger: Logger = logging.getLogger(__name__)

router = APIRouter()


def _get_cached(
        prompt: str,
        query_cache: LRUCache,
        db_session: Session,
) -> AskRecord | None:
    # maybe we already cached response for this query
    log_record: Optional[AskRecord] = query_cache.get(prompt)
    if log_record is not None:
        logger.debug("Serving from cache, query:'%s', response:'%s'",
                     prompt, log_record.response_text)
        return log_record

    # still, maybe we already answered this query previously
    query_hash = hash(prompt)
    log_record = get_record(db_session, query_hash)
    if log_record is not None and log_record.query_text == prompt:
        logger.info("Serving stored response: %s: %s", prompt, log_record.response_text)
        query_cache.put(prompt, log_record)
        # touch for LRU
        update_record(db_session, log_record)
        return log_record
    return None

@router.post("/ask", response_class=StreamingResponse)
async def ask(
    request: Request,
    prompt: AskRequest = Depends(query_middleware.validate_query),
    db_session: Session = Depends(db_middleware.get_db_session)
) -> HTMLResponse:
    """Makes requests to Ollama API Generate"""
    logger.info("Received ASK request from %s: %s", request.client, prompt.query)
    query_cache: LRUCache = request.app.state.query_cache
    ask_history_record: AskRecord | None = _get_cached(prompt.query, query_cache, db_session)
    if ask_history_record is not None:
        ask_history_record.clickable = False
        return templates.TemplateResponse(
            "ask_entry.html", {
                "request": request,
                "entry": ask_history_record
        })

    logger.info("Submitting generation request to the model: %s", prompt.query)
    bot_response_chunks: [str] = []
    response_chunk: str
    async for response_chunk in llm_api.ask(prompt.query):
        # accumulate chunks to persist history
        # TODO send chunks out as they arrive
        bot_response_chunks.append(response_chunk)
    ask_history_record: AskRecord = create_record(
        db_session,
        prompt.query,
        response_text="".join(bot_response_chunks),
    )
    if ask_history_record is None:
        logger.error('Failed to save new query record for "%s"', prompt.query)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="failed to persist query",
        )
    query_cache.put(prompt.query, ask_history_record)
    ask_history_record.clickable = False

    return templates.TemplateResponse(
        "ask_entry.html", {
            "request": request,
            "entry": ask_history_record,
        })
