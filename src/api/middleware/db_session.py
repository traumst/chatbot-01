"""DB connection wrapper around DB connection"""

import logging
from typing import Generator

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.db.database import SessionLocal

logger = logging.getLogger(__name__)


def get_db_session() -> Generator[Session, None, None]:
    """Middleware that provides active DB connection"""

    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.exception("Failed to acquire db session: %s", e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable OKPR"
        )
    finally:
        db.close()
