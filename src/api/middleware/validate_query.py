"""Middleware that validates the input query"""

import logging
from typing import Generator
from fastapi import Form, HTTPException, status
from pydantic import ValidationError

from src.schemas.gen_req import GenerationRequest

logger = logging.getLogger(__name__)


def validate_query(query_text: str = Form(...)) -> Generator[GenerationRequest, None, None]:
    """Assigns query text to an object with validation error handling"""

    try:
        yield GenerationRequest(query=query_text)
    except (ValueError, ValidationError) as e:
        logger.error("Query validation failed, %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid query: {e}"
        )
