"""
Chat with the model while keeping track of previous messages from each side - user and the bot.
"""

import logging
from logging import Logger

from fastapi import Request, Depends, APIRouter, HTTPException, status
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import src.api.middleware.db_session as db_middleware
import src.api.middleware.validate_query as query_middleware
import src.ollama.chat as chat
from src.db.tables import chat_record
from src.db.tables.chat_record import AuthorRole, ChatRecord
from src.schemas.ask_req import AskRequest

templates = Jinja2Templates(directory="src/template")

logger: Logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/convo", response_class=StreamingResponse)
async def convo(
    request: Request,
    prompt: AskRequest = Depends(query_middleware.validate_query),
    db_session: Session = Depends(db_middleware.get_db_session)
) -> HTMLResponse:
    """Back and forth messaging with history"""

    logger.info("Received CONVO request from %s: %s", request.client, prompt.query)
    logger.debug("Recording user message: %s", prompt.query)
    user_msg_record: ChatRecord = chat_record.create_record(
        db_session,
        chat_id=...,
        author=AuthorRole.USER,
        message=prompt.query,
    )
    logger.debug("Submitting messages to the model: %s", prompt.query)
    bot_msg_chunks: [str] = []
    async for response_chunk in chat.model_chat(prompt.query):
        # accumulate chunks to persist history
        # TODO send chunks out as they arrive
        bot_msg_chunks.append(response_chunk)
    logger.debug("Recording user message: %s", prompt.query)
    bot_msg_record: ChatRecord = chat_record.create_record(
        db_session,
        chat_id=...,
        author=AuthorRole.BOT,
        message="".join(bot_msg_chunks),
    )
    if bot_msg_record is None:
        logger.error('Failed to save new query record for "%s"', prompt.query)
        raise RuntimeError("failed to persist query for later")
    logger.debug("Templating chat response: %s", prompt.query)
    return templates.TemplateResponse(
        "chat_entry.html", {
            "request": request,
            "user_msg": user_msg_record,
            "bot_msg": bot_msg_record,
        })
