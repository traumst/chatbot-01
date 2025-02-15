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
    hash = Column(Integer, index=True) # for history lookup
    query_text = Column(Text, nullable=False)
    response_text = Column(Text)
    created_at = Column(DateTime, index=True, default=datetime.datetime.now(datetime.UTC))
    updated_at = Column(DateTime, index=True, nullable=True)

def create_query_log(
    db: Session,
    query: str,
    response_text: str = None
) -> QueryLog:
    """Creates new table entry and returns it"""

    db_log = QueryLog(
        hash=hash(query),
        query_text=query,
        response_text=response_text)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_query_log(db: Session, query_id: int) -> QueryLog | None:
    """
    Retrieves specific log by id

    :param db: db connection for the current user session
    :param query_id can be either id or hash value
    """

    one = db.query(QueryLog).filter(QueryLog.id == query_id or QueryLog.hash == query_id).first()
    if one is None:
        return None
    return one[0]


def get_query_logs(db: Session, offset: int = 0, limit: int = 20) -> List[QueryLog]:
    """
    Retrieves last entries, with optional offset and default limit of 20 with DESC order

    :param db: db connection for the current user session
    :param offset: skip over a number of elements
    :param limit: max count of entries to return
    """

    limit = 100 if limit > 100  else limit
    res = (db.query(QueryLog)
           .order_by(QueryLog.created_at.desc())
           .offset(offset)
           .limit(limit)
           .all())
    return cast(List[QueryLog], res)


def update_query_record(db: Session, query_log: QueryLog):
    query_log.updated_at = datetime.datetime.now()
    db.merge(query_log)
    db.commit()
    db.refresh(query_log)
    return query_log