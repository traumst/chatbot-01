"""DTO templates for conversation with the model"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel, Field, field_validator


class MessageRole(str, Enum):
    """Which side of the chat said what"""
    USER = 'user'
    BOT = 'bot'


class RawMessage(BaseModel):
    """
    Raw model response, excluding metadata.
    """

    role: MessageRole
    content: str = Field(..., min_length=9, max_length=1024)
    images: Optional[Any] = None

    class Config:
        arbitrary_types_allowed = True


class ChatMessage(BaseModel):
    """
    Ollama compatible model name to use and the user's prompt.
    """

    model: str = Field(..., min_length=9, max_length=50)
    messages: list[RawMessage]


class ChatResponse(BaseModel):
    """
    Intermediate model response, as indicated by 'done:false'.
    """

    model: str = Field(..., min_length=9, max_length=50)
    created_at: datetime
    message: RawMessage
    done: bool

    class Config:
        arbitrary_types_allowed = True

    def __eq__(self, other: object) -> bool:
        assert isinstance(other, ChatResponse)
        return self.created_at == other.created_at

    def __lt__(self, other: "ChatResponse") -> bool:
        if not isinstance(other, ChatResponse):
            raise RuntimeError(f"Incompatible type comparison to {type(other)}")
        return self.created_at < other.created_at

    def __gt__(self, other: "ChatResponse") -> bool:
        if not isinstance(other, ChatResponse):
            raise RuntimeError(f"Incompatible type comparison to {type(other)}")
        return self.created_at > other.created_at


class ChatResponseComplete(ChatResponse):
    """
    Final model response as indicated by 'done:true' and some metrics.
    """
    total_duration: timedelta
    load_duration: timedelta
    prompt_eval_count: int
    prompt_eval_duration: timedelta
    eval_count: int
    eval_duration: timedelta


    @field_validator(
        'total_duration',
        'load_duration',
        'prompt_eval_duration',
        'eval_duration',
        mode='before',
    )
    # TODO this breaks if I call it 'self' instead of 'cls', wonder why
    def convert_nanoseconds_to_timedelta(cls, nanoseconds: int) -> timedelta:
        """Converts from model's int nanoseconds to native timedelta"""

        return timedelta(seconds=float(nanoseconds) / 1e9)
