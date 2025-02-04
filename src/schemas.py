from pydantic import BaseModel
from datetime import datetime


class QueryLogBase(BaseModel):
    query_text: str


class QueryLogCreate(QueryLogBase):
    pass


class QueryLogResponse(QueryLogBase):
    id: int
    response_text: str = None
    created_at: datetime

    class Config:
        # orm_mode = True
        from_attributes = True
