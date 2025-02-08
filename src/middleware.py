from typing import Generator
from fastapi import Form

from pydantic import ValidationError
from sqlalchemy.orm import Session

from src.database import SessionLocal
from src.schemas.query_request import QueryRequest


def validate_query(query_text: str = Form(...)) -> Generator[QueryRequest, None, None]:
    """Middleware that validates the input query"""

    try:
        yield QueryRequest(query=query_text)
    except ValidationError as e:
        #log.error("Query validation failed, %s", e)
        return


def get_db() -> Generator[Session, None, None]:
    """Middleware that provides active DB connection"""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()