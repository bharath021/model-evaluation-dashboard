from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ModelSpec:
    provider: str
    model_name: str
    display_name: str


class LLMClient(Protocol):
    spec: ModelSpec

    @property
    def configured(self) -> bool:
        ...

    def generate(self, prompt: str) -> str:
        ...
