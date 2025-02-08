"""Models that define the data format in tables"""

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
