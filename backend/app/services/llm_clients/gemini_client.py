from typing import Any
from urllib.parse import quote

from backend.app.services.llm_clients.base import ModelSpec
from backend.app.services.llm_clients.errors import LLMProviderError
from backend.app.services.llm_clients.http import post_json


class GeminiClient:
    def __init__(self, model_name: str, api_key: str | None) -> None:
        self.spec = ModelSpec(
            provider="google",
            model_name=model_name,
            display_name="Gemini",
        )
        self.api_key = api_key

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def generate(self, prompt: str) -> str:
        encoded_model = quote(self.spec.model_name, safe="")
        data = post_json(
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{encoded_model}:generateContent",
            payload={"contents": [{"parts": [{"text": prompt}]}]},
            headers={"x-goog-api-key": self.api_key or ""},
        )
        text = _extract_text(data)
        if not text:
            raise LLMProviderError("Gemini returned no text output.")
        return text


def _extract_text(data: dict[str, Any]) -> str:
    chunks = []
    for candidate in data.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            if part.get("text"):
                chunks.append(part["text"])
    return "\n".join(chunks).strip()
