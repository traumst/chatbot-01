"""Operation that can be performed in the DB"""

from typing import cast, List
from sqlalchemy.orm import Session
from src.models import QueryLog
from src.schemas.query_request import QueryRequest


def create_query_log(
    db: Session,
    query_log: QueryRequest,
    response_text: str = None
) -> QueryLog:
    """Creates new table entry and returns it"""

    db_log = QueryLog(
        query_text=query_log.query,
        response_text=response_text)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_query_log(db: Session, query_id: int) -> QueryLog | None:
    """Retrieves specific log by id"""

    one = db.query(QueryLog).filter(QueryLog.id == query_id).first()
    if one is None:
        return None
    return one[0]


def get_query_logs(db: Session, skip: int = 0, limit: int = 10) -> List[QueryLog]:
    """Retrieves up-to specified number of entries after offset"""

    res = db.query(QueryLog).offset(skip).limit(limit).all()
    return cast(List[QueryLog], res)
