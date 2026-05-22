from datetime import datetime

from pydantic import BaseModel, Field


class EvalRunRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=12_000)


class ScoreSet(BaseModel):
    relevance: int = Field(ge=0, le=10)
    clarity: int = Field(ge=0, le=10)
    length: int = Field(ge=0, le=10)


class ModelResponseRecord(BaseModel):
    id: int
    model_name: str
    response_text: str
    scores: ScoreSet
    response_time_ms: int = Field(ge=0)
    created_at: datetime


class EvalRunResponse(BaseModel):
    id: int
    prompt: str
    created_at: datetime
    responses: list[ModelResponseRecord]
