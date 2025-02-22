from datetime import datetime, timedelta
from typing import List

from pydantic import BaseModel, Field, field_validator

# curl http://localhost:11434/api/generate -d '{
#   "model": "deepseek-r1:1.5b",
#   "prompt":"Why is the sky blue?"
# }' -i
class GenerationRequest(BaseModel):
    model: str = Field(..., min_length=9, max_length=50)
    prompt: str = Field(str, min_length=9, max_length=1024)

# {
#   "model":"deepseek-r1:1.5b",
#   "created_at":"2025-02-20T22:01:10.664459Z",
#   "response":" affect",
#   "done":false
# }
class GenerationResponse(BaseModel):
    model: str = Field(..., min_length=9, max_length=50)
    created_at: datetime
    response: str
    done: bool

    def __lt__(self, other: "GenerationResponse") -> bool:
        if not isinstance(other, GenerationResponse):
            return NotImplemented
        return self.created_at < other.created_at

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GenerationResponse):
            return NotImplemented
        return self.created_at == other.created_at


# {
#   "model":"deepseek-r1:1.5b",
#   "created_at":"2025-02-20T22:01:10.716564Z",
#   "response":"",
#   "done":true,
#   "done_reason":"stop",
#   "context":[151644,10234,374,279,12884,6303,30,151645,151648,271,151649,271,785,1894,315,279,12884,11,476,1181,6303,11094,11,374,264,1102,315,3807,9363,3238,3786,13,3197,39020,28833,279,9237,594,16566,11,432,16211,1526,5257,13617,323,24491,279,9237,594,7329,13,1634,39020,83161,448,18730,304,279,16566,11,1741,438,23552,34615,504,279,3720,11,1493,21880,646,5240,3100,311,44477,13,1096,71816,1882,3059,304,279,2518,476,6303,1894,3881,438,330,40384,774,81002,367,1189,8697,3100,1136,10175,803,1091,2518,3100,4152,311,1181,23327,45306,13,15277,11,279,12884,7952,6303,1576,6303,3100,374,36967,1393,2518,323,18575,3100,16211,1526,803,6707,382,1986,24844,374,264,949,315,279,26829,12344,3920,315,21372,774,26443,323,279,9237,594,16566,11,892,14758,3170,9104,4682,646,7802,9434,7987,13],
#   "total_duration":2143499292,
#   "load_duration":30846417,
#   "prompt_eval_count":9,
#   "prompt_eval_duration":138000000,
#   "eval_count":153,
#   "eval_duration":1973000000
# }
class GenerationResponseComplete(GenerationResponse):
    done_reason: str
    context: List[int]
    total_duration: timedelta
    load_duration: timedelta
    prompt_eval_count: int
    prompt_eval_duration: timedelta
    eval_count: int
    eval_duration: timedelta

    @field_validator('total_duration', 'load_duration', 'prompt_eval_duration', 'eval_duration', mode='before')
    def convert_nanoseconds_to_timedelta(cls, value: int):
        return timedelta(seconds=float(value) / 1e9)