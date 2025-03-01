"""
Chat with the model while keeping track of previous messages from each side - user and the bot.
"""
import logging
from logging import Logger
from typing import List

from fastapi import Request, Depends, APIRouter
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session

import src.ollama.chat as model
from src.api.middleware.db_session import get_db_session
from src.api.middleware.validate_chat_id import lock_chat_id
from src.api.middleware.validate_query import validate_query
from src.db.tables import chat_record
from src.db.tables.chat_record import AuthorRole, ChatRecord
from src.ollama.chat_models import RawMessage
from src.schemas.ask_req import AskRequest
from src.utils.lru_cache import LRUCache

templates = Jinja2Templates(directory="src/template")

logger: Logger = logging.getLogger(__name__)

router = APIRouter()

class CachedChat(BaseModel):
    """Represents chat cached in-memory"""

    chat_id: int
    messages: List[ChatRecord] = []

    class Config:
        arbitrary_types_allowed = True

def format_cache_id(chat_id: int) -> str:
    """Formats chat_id to cache-friendly string"""

    return f"chat:{chat_id}"

@router.post("/chat", response_class=StreamingResponse)
async def chat(
    request: Request,
    chat_id: int = Depends(lock_chat_id),
    chat_query: AskRequest = Depends(validate_query),
    db_session: Session = Depends(get_db_session),
) -> HTMLResponse:
    """Back and forth messaging with history"""

    logger.info("Received CHAT request from %s: %s", request.client, chat_query.query)
    cache: LRUCache = request.app.state.query_cache
    history: CachedChat = cache.get(format_cache_id(chat_id))
    if history is None or len(history.messages) < 1:
        logger.debug("Chat %d history is loaded from db", chat_id)
        messages: list[ChatRecord] = chat_record.get_records(
            db_session,
            chat_id,
            offset=0,
            limit=100,
        )
        history = CachedChat(chat_id=chat_id, messages=messages)
        cache.put(format_cache_id(chat_id), history)

    logger.info("Chat %d seem to have %d messages so far", chat_id, len(history.messages))
    user_msg: ChatRecord = chat_record.create_record(
        db_session,
        chat_id=chat_id,
        author=AuthorRole.USER,
        message=chat_query.query.strip(),
    )
    history.messages.append(user_msg)

    logger.debug("Submitting query to the model: '%s' %d", chat_query.query.strip(), len(history.messages))
    messages: List[RawMessage] = [RawMessage(
        role=msg.author,
        content=msg.message,
    ) for msg in history.messages]
    bot_msg_chunks: [str] = []
    async for response_chunk in model.chat(messages):
        # accumulate chunks to persist history
        bot_msg_chunks.append(response_chunk)

    logger.debug("Recording bot message: %s", chat_query.query)
    bot_msg: ChatRecord = chat_record.create_record(
        db_session,
        chat_id=chat_id,
        author=AuthorRole.BOT,
        message="".join(bot_msg_chunks),
    )
    history.messages.append(bot_msg)

    logger.debug("Templating response: %s", chat_query.query)
    template = templates.get_template("chat_entry.j2")
    rendered2 = template.render(request=request, entry=bot_msg, AuthorRole=AuthorRole)
    rendered1 = template.render(request=request, entry=user_msg, AuthorRole=AuthorRole)

    return HTMLResponse(content=rendered1 + rendered2)
