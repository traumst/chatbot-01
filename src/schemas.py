"""This module defines the shape of requests and responses"""

from datetime import datetime
from pydantic import BaseModel


class QueryRequest(BaseModel):
    """Request format accepted by the API"""
    query_text: str = None


class QueryResponse(BaseModel):
    """Response format returned from the API"""
    id: int
    response_text: str = None
    created_at: datetime
