from backend.app.core.config import Settings
from backend.app.services.llm_clients.anthropic_client import AnthropicClient
from backend.app.services.llm_clients.base import LLMClient, ModelSpec
from backend.app.services.llm_clients.gemini_client import GeminiClient
from backend.app.services.llm_clients.mock_client import MockLLMClient
from backend.app.services.llm_clients.openai_client import OpenAIClient


def build_clients(settings: Settings) -> list[LLMClient]:
    if settings.llm_mode == "live":
        return [
            OpenAIClient(settings.openai_model, settings.openai_api_key),
            AnthropicClient(settings.anthropic_model, settings.anthropic_api_key),
            GeminiClient(settings.gemini_model, settings.gemini_api_key),
        ]

    return [
        MockLLMClient(
            ModelSpec(
                provider="openai",
                model_name=settings.openai_model,
                display_name="OpenAI",
            )
        ),
        MockLLMClient(
            ModelSpec(
                provider="anthropic",
                model_name=settings.anthropic_model,
                display_name="Claude",
            )
        ),
        MockLLMClient(
            ModelSpec(
                provider="google",
                model_name=settings.gemini_model,
                display_name="Gemini",
            )
        ),
    ]
