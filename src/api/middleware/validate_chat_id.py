"""Middleware that validates the input query"""

import asyncio
import logging
from typing import Generator, AsyncGenerator

from fastapi import Form, HTTPException, status, Depends, Request

logger = logging.getLogger(__name__)

async def get_chat_lock(app, chat_id: int) -> asyncio.Lock:
    """Acquires lock on specific chat id"""

    async with app.state.global_lock:
        if chat_id not in app.state.chat_locks:
            app.state.chat_locks[chat_id] = asyncio.Lock()
        return app.state.chat_locks[chat_id]


def validate_chat_id(chat_id: int = Form(...)) -> Generator[int, None, None]:
    """Assigns query text to an object with validation error handling"""

    if chat_id < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    yield chat_id


async def lock_chat_id(
        chat_id: int = Depends(validate_chat_id),
        request: Request = None,
) -> AsyncGenerator[int, None]:
    """
    Attempts to lock chat for modification with a timeout.
    Yields valid chat_id if lock is successful.
    In case of timeout - bounces user off with 503 Service Unavailable.
    """

    lock = await get_chat_lock(request.app, chat_id)
    try:
        await asyncio.wait_for(lock.acquire(), timeout=0.1)
        yield chat_id
    except asyncio.TimeoutError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Resource busy. Please try again later."
        ) from e
    finally:
        lock.release()
