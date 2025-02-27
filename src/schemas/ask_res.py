"""Response format returned from the Generate API"""

from datetime import datetime
from pydantic import BaseModel


class AskResponse(BaseModel):
    """Expected response format"""

    id: int
    response: str = None
    timestamp: datetime
