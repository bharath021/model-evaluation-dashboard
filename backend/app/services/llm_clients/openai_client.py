from typing import Any

from backend.app.services.llm_clients.base import ModelSpec
from backend.app.services.llm_clients.errors import LLMProviderError
from backend.app.services.llm_clients.http import post_json


class OpenAIClient:
    def __init__(self, model_name: str, api_key: str | None) -> None:
        self.spec = ModelSpec(
            provider="openai",
            model_name=model_name,
            display_name="OpenAI",
        )
        self.api_key = api_key

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def generate(self, prompt: str) -> str:
        data = post_json(
            "https://api.openai.com/v1/responses",
            payload={"model": self.spec.model_name, "input": prompt},
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        text = _extract_output_text(data)
        if not text:
            raise LLMProviderError("OpenAI returned no text output.")
        return text


def _extract_output_text(data: dict[str, Any]) -> str:
    chunks = []
    for item in data.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text" and content.get("text"):
                chunks.append(content["text"])
    return "\n".join(chunks).strip()
