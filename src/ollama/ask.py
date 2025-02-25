"""
Calls local Ollama '/api/generate'

https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-completion
"""

import json
import logging
from json import JSONDecodeError
from typing import Optional, AsyncGenerator

import httpx
from pydantic import ValidationError

from src.ollama.ask_models import GenerationRequest, GenerationResponse, GenerationResponseComplete
from src.utils.env_config import read_env, EnvConfig

logger = logging.getLogger(__name__)

def _parse_generation_line(line: str) -> GenerationResponse:
    """
    Parse a JSON line into the appropriate GenerationResponse object.

    :raises ValueError: if json parsing or validation fails
    """
    try:
        data = json.loads(line)
        if "done_reason" in data:
            return GenerationResponseComplete.model_validate(data)
        return GenerationResponse.model_validate(data)
    except JSONDecodeError as e:
        raise ValueError("Failed to decode JSON") from e
    except ValidationError as e:
        raise ValueError("Validation failed for response data") from e

async def _model_generate(
    prompt: str
) -> AsyncGenerator[Optional[GenerationResponse | ValueError], None]:
    """
    Asynchronously yields generated responses chunk by chunk

    :raises ValueError: if json parsing or validation fails
    """
    conf: EnvConfig = read_env()
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            f"{conf.model_url}api/generate",
            json=GenerationRequest(model=conf.model_name, prompt=prompt).model_dump()
        ) as response:
            # iterate over lines as they come
            async for raw_line in response.aiter_lines():
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    parsed_response = _parse_generation_line(line)
                    print(f"raw model response {parsed_response.response=}")
                    yield parsed_response
                except ValueError as e:
                    logger.error("Failed to parse response chunk: %s, %s", line, e)
                    yield e

async def ask(query: str) -> AsyncGenerator[str, None]:
    """Ask model to process single user query - i.e. no history"""

    max_acc_len: int = 8192
    acc_len: int = 0
    part: GenerationResponse | ValueError
    async for part in _model_generate(query):
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
