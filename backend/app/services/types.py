from dataclasses import dataclass


@dataclass(frozen=True)
class Scores:
    relevance: int
    clarity: int
    length: int


@dataclass(frozen=True)
class GeneratedModelResponse:
    model_name: str
    response_text: str
    scores: Scores
    response_time_ms: int
