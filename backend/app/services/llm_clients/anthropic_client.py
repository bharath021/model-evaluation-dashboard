from typing import Any

from backend.app.services.llm_clients.base import ModelSpec
from backend.app.services.llm_clients.errors import LLMProviderError
from backend.app.services.llm_clients.http import post_json


class AnthropicClient:
    def __init__(self, model_name: str, api_key: str | None) -> None:
        self.spec = ModelSpec(
            provider="anthropic",
            model_name=model_name,
            display_name="Claude",
        )
        self.api_key = api_key

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def generate(self, prompt: str) -> str:
        data = post_json(
            "https://api.anthropic.com/v1/messages",
            payload={
                "model": self.spec.model_name,
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}],
            },
            headers={
                "x-api-key": self.api_key or "",
                "anthropic-version": "2023-06-01",
            },
        )
        text = _extract_text(data)
        if not text:
            raise LLMProviderError("Anthropic returned no text output.")
        return text


def _extract_text(data: dict[str, Any]) -> str:
    return "\n".join(
        block["text"]
        for block in data.get("content", [])
        if block.get("type") == "text" and block.get("text")
    ).strip()
