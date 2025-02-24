"""Wrapper for the Ollama API Generate"""
import logging
from logging import Logger
from typing import AsyncGenerator

from src.llm import ollama
from src.utils.env_config import read_env, EnvConfig
from src.utils.logmod import init as init_log
from src.utils.lru_cache import LRUCache

runtime_config: EnvConfig = read_env()
query_cache = LRUCache(size=runtime_config.cache_size)
init_log(runtime_config.log_level)

logger: Logger = logging.getLogger(__name__)

async def generate(query: str) -> AsyncGenerator[str, None]:
    """Generates response to user query"""

    max_acc_len: int = 10000
    acc_len: int = 0
    async for part in ollama.generate(query):
        if part is None:
            logger.warning("error occurred while generating response for '%s'", query)
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
