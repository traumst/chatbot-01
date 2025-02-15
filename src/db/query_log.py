"""Operation that can be performed in the DB"""

from typing import cast, List
from sqlalchemy.orm import Session

import datetime
from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class QueryLog(Base):
    """Represents request-response pair"""

    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    response_text = Column(Text)  # Could be null until processed
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))


def create_query_log(
    db: Session,
    query: str,
    response_text: str = None
) -> QueryLog:
    """Creates new table entry and returns it"""

    db_log = QueryLog(
        query_text=query,
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


def get_query_logs(db: Session, offset: int = 0, limit: int = 20) -> List[QueryLog]:
    """Retrieves last entries, with optional offset and default limit of 20"""

    res = db.query(QueryLog).order_by(QueryLog.created_at.desc()).offset(offset).limit(limit).all()
    return cast(List[QueryLog], res)
