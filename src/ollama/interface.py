"""
Wrapper for the Ollama API "Generate" Request

https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-completion
"""

import logging
from typing import AsyncGenerator

from src.ollama.ask_models import GenerationResponse
import src.ollama.ask_util as ask_util

logger = logging.getLogger(__name__)

async def ask(query: str) -> AsyncGenerator[str, None]:
    """Ask model to process single user query - i.e. no history"""

    max_acc_len: int = 8192
    acc_len: int = 0
    part: GenerationResponse | ValueError
    async for part in ask_util.model_generate(query):
        if part is None:
            logger.warning("none returned while generating response for '%s'", query)
            continue

        if part is ValueError:
            logger.error("error occurred while generating response for '%s', %s", query, part)
            continue

        if hasattr(part, "response"):
            acc_len += len(part.response)
            yield part.response

        if acc_len >= max_acc_len:
            logger.info("response reached max len for query '%s'", query)
            return

async def chat(message: str) -> AsyncGenerator[str, None]:
    """Initiate or continue chat with a model"""

    max_acc_len: int = 1024
    acc_len: int = 0
    part: ChatResponse | ValueError
    async for part in ask_util.model_chat(query):
        if part is None:
            logger.warning("none returned while generating response for '%s'", query)
            continue

        if part is ValueError:
            logger.error("error occurred while generating response for '%s', %s", query, part)
            continue

        if hasattr(part, "response"):
            acc_len += len(part.response)
            yield part.response

        if acc_len >= max_acc_len:
            logger.info("response reached max len for query '%s'", query)
            return