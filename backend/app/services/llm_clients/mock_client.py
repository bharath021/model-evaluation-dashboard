from backend.app.services.llm_clients.base import ModelSpec


class MockLLMClient:
    def __init__(self, spec: ModelSpec) -> None:
        self.spec = spec

    @property
    def configured(self) -> bool:
        return True

    def generate(self, prompt: str) -> str:
        return (
            f"{self.spec.display_name} mock response for local development. "
            f"It received the evaluation prompt: {prompt.strip()} "
            "Switch LLM_MODE to live and add provider API keys for real model output."
        )
