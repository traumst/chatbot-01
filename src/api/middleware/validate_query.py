import logging
from typing import Generator
from fastapi import Form
from pydantic import ValidationError
from src.schemas.generation_request import GenerationRequest

logger = logging.getLogger(__name__)


def validate_query(query_text: str = Form(...)) -> Generator[GenerationRequest, None, None]:
    """Middleware that validates the input query"""

    try:
        yield GenerationRequest(query=query_text)
    except ValidationError as e:
        logger.error("Query validation failed, %s", e)
        return