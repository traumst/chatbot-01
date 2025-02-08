from pydantic import BaseModel, field_validator


class QueryRequest(BaseModel):
    """Request format accepted by the API"""

    query: str = None

    @classmethod
    @field_validator("query")
    def text_must_not_be_empty(cls, value: str):
        """Ensure query string is non-empty"""

        if value is None or not value or not value.strip():
            raise ValueError("query is empty")
        return value
