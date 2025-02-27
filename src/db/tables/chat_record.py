"""Record of messages between user and the model"""

from datetime import datetime, UTC
import logging
import enum
from typing import List
from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy import func, select, inspect
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, ColumnProperty

logger = logging.getLogger(__name__)

Base = declarative_base()


class AuthorRole(str, enum.Enum):
    """Which side of the chat said what"""
    USER = 'user'
    BOT = 'bot'


class ChatRecord(Base):
    """Represents request-response pair"""

    __tablename__ = "chat_record"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, index=True)
    author = Column(sqlalchemy.Enum(AuthorRole), index=True)
    hash = Column(Integer, index=True) # for history lookup
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, index=True, default=datetime.now(UTC))
    updated_at = Column(DateTime, index=True, nullable=True)

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


def create_record(
    db: Session,
    chat_id: int,
    author: AuthorRole,
    message: str = None,
) -> ChatRecord:
    """Creates new table entry and returns it"""

    db_log = ChatRecord(
        chat_id=chat_id,
        author=author,
        hash=hash(message),
        message=message,
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_record(db: Session, rec_id: int) -> ChatRecord | None:
    """
    Retrieves specific log by id

    :param db: db connection for the current user session
    :param rec_id: record id or hash
    """

    one = db.query(ChatRecord).filter(ChatRecord.id == rec_id).first()
    # logger.error(f"Query log record found [{one.__repr__()}]")
    return one


def get_records(db: Session, offset: int = 0, limit: int = 20) -> List[ChatRecord]:
    """
    Retrieves last entries, with optional offset and default limit of 20 with DESC order.
    Request and response fields are limited to 60 chars.

    :param db: db connection for the current user session
    :param offset: skip over a number of elements
    :param limit: max count of entries to return
    """

    limit = 100 if limit > 100 else limit
    stmt = select(
        ChatRecord.id,
        ChatRecord.hash,
        ChatRecord.author,
        func.substr(ChatRecord.message, 1, 60).label("response_text"),
        ChatRecord.created_at,
        ChatRecord.updated_at,
    ).order_by(
        ChatRecord.created_at.desc()
    ).offset(offset).limit(limit)

    result = db.execute(stmt)
    rows = result.mappings().all()
    logs = [ChatRecord(**row) for row in rows]

    return logs


def update_record(db: Session, record: ChatRecord):
    """
    Synchronizes instance values with corresponding db record.
    Always overwrites `updated_at` to the current time.

    :param db: db connection for the current user session
    :param record: request-response pair
    """

    record.updated_at = datetime.now()
    db.merge(record)
    db.commit()
    db.refresh(record)
    return record
