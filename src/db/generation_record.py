"""Operation that can be performed in the DB"""
import datetime
import logging
from typing import List

from sqlalchemy import event, Column, Integer, Text, DateTime, inspect
from sqlalchemy import func, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, ColumnProperty

logger = logging.getLogger(__name__)

Base = declarative_base()

class GenerationRecord(Base):
    """Represents request-response pair"""

    __tablename__ = "generation_record"

    id = Column(Integer, primary_key=True, index=True)
    hash = Column(Integer, index=True) # for history lookup
    query_text = Column(Text, nullable=False)
    response_text = Column(Text)
    created_at = Column(DateTime, index=True, default=datetime.datetime.now(datetime.UTC))
    updated_at = Column(DateTime, index=True, nullable=True)
    clickable = True

    def to_dict(self):
        """Serialize this instance into dict"""

        mapper = inspect(self).mapper
        return {
            prop.key: getattr(self, prop.key)
            for prop in mapper.attrs # type: ignore[attr-defined]
            if isinstance(prop, ColumnProperty)
        }

    def __repr__(self):
        return f"{self.__class__.__name__}({self.to_dict()})"

@event.listens_for(GenerationRecord, 'load')
def receive_load(target, _):
    """Makes every object loaded from the DB clickable by default"""

    target.clickable = True

def create_query_log(
    db: Session,
    query: str,
    response_text: str = None
) -> GenerationRecord:
    """Creates new table entry and returns it"""

    db_log = GenerationRecord(
        hash=hash(query),
        query_text=query,
        response_text=response_text)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_record(db: Session, query_id: int) -> GenerationRecord | None:
    """
    Retrieves specific log by id

    :param db: db connection for the current user session
    :param query_id can be either id or hash value
    """

    one = db.query(GenerationRecord).filter(GenerationRecord.id == query_id).first()
    # logger.error(f"Query log record found [{one.__repr__()}]")
    return one


def get_records(db: Session, offset: int = 0, limit: int = 20) -> List[GenerationRecord]:
    """
    Retrieves last entries, with optional offset and default limit of 20 with DESC order.
    Request and response fields are limited to 60 chars.

    :param db: db connection for the current user session
    :param offset: skip over a number of elements
    :param limit: max count of entries to return
    """

    limit = 100 if limit > 100 else limit
    stmt = select(
        GenerationRecord.id,
        GenerationRecord.hash,
        func.substr(GenerationRecord.query_text, 1, 60).label("query_text"),
        func.substr(GenerationRecord.response_text, 1, 60).label("response_text"),
        GenerationRecord.created_at,
        GenerationRecord.updated_at,
    ).order_by(GenerationRecord.created_at.desc()).offset(offset).limit(limit)

    result = db.execute(stmt)
    rows = result.mappings().all()
    logs = [GenerationRecord(**row) for row in rows]

    return logs


def update_query_record(db: Session, record: GenerationRecord):
    """
    Synchronizes instance values with corresponding db record.
    Always overwrites `updated_at` to the current time.

    :param db: db connection for the current user session
    :param record: request-response pair
    """

    record.updated_at = datetime.datetime.now()
    db.merge(record)
    db.commit()
    db.refresh(record)
    return record