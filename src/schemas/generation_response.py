from datetime import datetime
from pydantic import BaseModel


class GenerationResponse(BaseModel):
    """Response format returned from the API"""

    id: int
    response: str = None
    timestamp: datetime
