"""
Calls local Ollama via http api

https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-completion
"""
import json
import logging
from json import JSONDecodeError
from typing import AsyncGenerator, Dict

import httpx
from pydantic import ValidationError

from src.ollama.chat_models import (
    ChatResponse, ChatResponseComplete, ChatMessage,
    RawMessage, MessageRole)
from src.utils.env_config import EnvConfig, read_env
from src.utils.lru_cache import LRUCache

logger = logging.getLogger(__name__)

env: EnvConfig = read_env()
# TODO limit per user per chat max history
shared_cache = LRUCache(size=env.cache_size)


def _parse_line(line: str) -> ChatResponse:
    """
    Parse a JSON line into the appropriate ChatResponse object.

    :raises ValueError: if json parsing or validation fails
    """
    try:
        data = json.loads(line)
        if "done_reason" in data:
            return ChatResponseComplete.model_validate(data)
        return ChatResponse.model_validate(data)
    except JSONDecodeError as e:
        raise ValueError("Failed to decode JSON") from e
    except ValidationError as e:
        raise ValueError("Validation failed for response data") from e

async def _model_chat(
    prompt: str,
    conf: EnvConfig,
) -> AsyncGenerator[ChatResponse | ValueError, None]:
    """
    Asynchronously yields generated responses chunk by chunk

    :raises ValueError: if json parsing or validation fails
    """
    # TODO get chat history
    messages: [RawMessage] = [RawMessage(role=MessageRole.USER,content=prompt)]
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            f"{conf.model_url}api/generate",
            json=ChatMessage(model=conf.model_name, messages=messages).model_dump()
        ) as response:
            # iterate over lines as they come
            async for raw_line in response.aiter_lines():
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    parsed_response: ChatResponse = _parse_line(line)
                    print(f"raw model response {parsed_response.response=}")
                    yield parsed_response
                except ValueError as e:
                    logger.error("Failed to parse response chunk: %s, %s", line, e)
                    yield e

async def chat(query: str) -> AsyncGenerator[str, None]:
    """Ask model to initiate or continue chat with user - i.e. with history"""

    max_acc_len: int = 8192
    acc_len: int = 0
    part: ChatResponse | ValueError
    async for part in _model_chat(query, conf=env):
        if part is None:
            logger.warning("none returned while generating chat for '%s'", query)
            continue

        if part is ValueError:
            logger.error("error occurred while generating chat for '%s', %s", query, part)
            continue

        if hasattr(part, "response"):
            acc_len += len(part.response)
            yield part.response

        if acc_len >= max_acc_len:
            logger.info("response reached max len for query '%s'", query)
            return
