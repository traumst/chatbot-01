from typing import Generator
from fastapi import Form
from pydantic import ValidationError
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.schemas.query_request import QueryRequest
from src.utils.logger import logger
from src.utils.lru_cache import LRUCache

cache = LRUCache(size=4, purge_ratio=0.5)

def validate_query(query_text: str = Form(...)) -> Generator[QueryRequest, None, None]:
    """Middleware that validates the input query"""

    try:
        yield QueryRequest(query=query_text)
    except ValidationError as e:
        logger.error("Query validation failed, %s", e)
        return


def get_db() -> Generator[Session, None, None]:
    """Middleware that provides active DB connection"""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()