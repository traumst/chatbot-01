import logging
from typing import Generator
from sqlalchemy.orm import Session
from src.db.database import SessionLocal

logger = logging.getLogger(__name__)


def get_db() -> Generator[Session, None, None]:
    """Middleware that provides active DB connection"""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()