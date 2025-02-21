import json
import logging
from json import JSONDecodeError

import httpx
from typing import Optional, AsyncGenerator, Union

from pydantic import ValidationError

from src.utils.env_config import read_env, EnvConfig
from src.llm.models import GenerationRequest, GenerationResponse, GenerationResponseComplete

logger = logging.getLogger(__name__)

def parse_generation_line(line: str) -> GenerationResponse:
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

async def generate(prompt: str) -> AsyncGenerator[Optional[GenerationResponse | ValueError], None]:
    """
    Asynchronously yields generated responses chunk by chunk.

    :raises ValueError: if json parsing or validation fails
    """
    conf: EnvConfig = read_env()
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            conf.model_url.path,
            json=GenerationRequest(model=conf.model_name, prompt=prompt)
        ) as response:
            async for raw_line in response.aiter_lines():
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    parsed_response = parse_generation_line(line)
                    yield parsed_response
                except ValueError as e:
                    logger.error("Failed to parse response chunk: %s, %s", line, e)