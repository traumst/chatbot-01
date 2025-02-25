"""DTO templates for conversation with the model"""

from datetime import datetime, timedelta
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class ChatMessage(BaseModel):
    """
    Ollama compatible model name to use and user's prompt.

    example:
        curl http://localhost:11434/api/chat -d '{
          "model": "deepseek-r1:8b",
          "messages": [
            {
              "role": "user",
              "content": "why is the sky blue?"
            }
          ]
        }'
    """

    model: str = Field(..., min_length=9, max_length=50)
    prompt: str = Field(str, min_length=9, max_length=1024)

class MessageRole(str, Enum):
    """Which side of the chat said what"""
    USER = 'user'
    BOT = 'assistant'

class RawMessage(BaseModel):
    """
    Raw model response, excluding metadata.
    """

    role: MessageRole
    content: str = Field(..., min_length=9, max_length=1024)
    images: any = None


class ChatResponse(BaseModel):
    """
    Intermediate model response, as indicated by 'done:false'.

    example:
        {
          "model": "deepseek-r1:8b",
          "created_at": "2023-08-04T08:52:19.385406455-07:00",
          "message": {
            "role": "assistant",
            "content": "The",
            "images": null
          },
          "done": false
        }
    """

    model: str = Field(..., min_length=9, max_length=50)
    created_at: datetime
    message: RawMessage
    done: bool

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

    example:
        {
          "model": "deepseek-r1:8b",
          "created_at": "2023-08-04T19:22:45.499127Z",
          "done": true,
          "total_duration": 4883583458,
          "load_duration": 1334875,
          "prompt_eval_count": 26,
          "prompt_eval_duration": 342546000,
          "eval_count": 282,
          "eval_duration": 4535599000
        }
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
    def convert_nanoseconds_to_timedelta(self, nanoseconds: int) -> timedelta:
        """Converts from model's int nanoseconds to native timedelta"""

        return timedelta(seconds=float(nanoseconds) / 1e9)
