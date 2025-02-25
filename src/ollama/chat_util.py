"""
Calls local Ollama via http api

https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-completion
"""

import logging
from typing import Optional, AsyncGenerator

from src.ollama.ask_models import GenerationResponse

logger = logging.getLogger(__name__)

async def model_chat(
    prompt: str
) -> AsyncGenerator[Optional[GenerationResponse | ValueError], None]:
    pass