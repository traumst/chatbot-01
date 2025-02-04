"""Operation that can be performed in the DB"""

from typing import List
from sqlalchemy.orm import Session
from src import models, schemas


def create_query_log(
    db: Session,
    query_log: schemas.QueryRequest,
    response_text: str = None
) -> models.QueryLog:
    """Creates new table entry and returns it"""

    db_log = models.QueryLog(
        query_text=query_log.query_text,
        response_text=response_text)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_query_log(db: Session, query_id: int) -> models.QueryLog:
    """Retrieves specific log by id"""

    return db.query(models.QueryLog).filter(models.QueryLog.id == query_id).first()


def get_query_logs(db: Session, skip: int = 0, limit: int = 10) -> List[models.QueryLog]:
    """Retrieves up-to specified number of entries from offset"""

    return db.query(models.QueryLog).offset(skip).limit(limit).all()
