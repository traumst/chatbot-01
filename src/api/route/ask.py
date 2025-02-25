"""
One-off shot query to the model with all context provided in a single prompt
"""

import datetime
import logging
from logging import Logger
from typing import Optional

from fastapi import Request, Depends, APIRouter
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import src.api.middleware.db_session as db_middleware
import src.api.middleware.validate_query as query_middleware
import src.ollama.ask as llm_api
from src.db import generation_record
from src.db.generation_record import GenerationRecord
from src.schemas.gen_req import GenerationRequest
from src.utils.lru_cache import LRUCache

templates = Jinja2Templates(directory="src/template")

logger: Logger = logging.getLogger(__name__)

router = APIRouter()


def _get_cached(
        prompt: str,
        query_cache: LRUCache,
        db_session: Session,
) -> GenerationRecord | None:
    # maybe we already cached response for this query
    log_record: Optional[GenerationRecord] = query_cache.get(prompt.query)
    if log_record is not None:
        logger.debug("Serving from cache, query:'%s', response:'%s'",
                     prompt, log_record.response_text)
        return log_record

    # still, maybe we already answered this query previously
    query_hash = hash(prompt)
    log_record = generation_record.get_record(db_session, query_hash)
    if log_record is not None and log_record.query_text == prompt:
        logger.info("Serving stored response: %s: %s", prompt, log_record.response_text)
        query_cache.put(prompt, log_record)
        log_record.updated_at = datetime.datetime.now()
        generation_record.update_query_record(db_session, log_record)
        return log_record
    return None

@router.post("/ask", response_class=StreamingResponse)
async def ask(
    request: Request,
    prompt: GenerationRequest = Depends(query_middleware.validate_query),
    db_session: Session = Depends(db_middleware.get_db_session)
) -> HTMLResponse:
    """Makes requests to Ollama API Generate"""
    logger.info("Received ASK request from %s: %s", request.client, prompt.query)
    query_cache: LRUCache = request.app.state.query_cache
    query_log_record: GenerationRecord | None = _get_cached(prompt.query, query_cache, db_session)
    if query_log_record is not None:
        query_log_record.clickable = False
        return templates.TemplateResponse(
            "log_entry.html", {
                "request": request,
                "entry": query_log_record
        })

    logger.info("Making generation request: %s", )
    responses: [str] = []
    async for part in llm_api.ask(prompt.query):
        # TODO send chunks as they arrive
        responses.append(part)

    # store and cache for reuse
    query_log_record: GenerationRecord = generation_record.create_query_log(
        db_session,
        prompt.query,
        response_text="".join(responses),
    )
    if query_log_record is None:
        logger.error('Failed to save new query record for "%s"', prompt.query)
        raise RuntimeError("failed to persist query for later")
    query_cache.put(prompt.query, query_log_record)
    query_log_record.clickable = False

    return templates.TemplateResponse(
        "log_entry.html", {
            "request": request,
            "entry": query_log_record,
        })
