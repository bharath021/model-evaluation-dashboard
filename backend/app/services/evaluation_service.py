import asyncio
from time import perf_counter
from typing import Any

from backend.app.db.repository import EvaluationRepository
from backend.app.services.llm_clients.base import LLMClient
from backend.app.services.llm_clients.errors import LLMProviderError
from backend.app.services.scoring_service import ResponseScorer
from backend.app.services.types import GeneratedModelResponse


class EvaluationService:
    def __init__(
        self,
        repository: EvaluationRepository,
        clients: list[LLMClient],
        scorer: ResponseScorer,
        llm_mode: str,
    ) -> None:
        self.repository = repository
        self.clients = clients
        self.scorer = scorer
        self.llm_mode = llm_mode

    async def run_evaluation(self, prompt: str) -> dict[str, Any]:
        generated = await asyncio.gather(
            *(self._generate_response(client, prompt) for client in self.clients)
        )
        return self.repository.create_run(prompt=prompt, responses=generated)

    def get_history(self, limit: int) -> list[dict[str, Any]]:
        return self.repository.list_runs(limit=limit)

    def get_available_models(self) -> list[dict[str, Any]]:
        return [
            {
                "provider": client.spec.provider,
                "model_name": client.spec.model_name,
                "display_name": client.spec.display_name,
                "configured": client.configured,
                "mode": self.llm_mode,
            }
            for client in self.clients
        ]

    async def _generate_response(
        self,
        client: LLMClient,
        prompt: str,
    ) -> GeneratedModelResponse:
        if not client.configured:
            raise LLMProviderError(
                f"{client.spec.display_name} is not configured. "
                "Use mock mode or provide its API key."
            )

        started_at = perf_counter()
        response_text = await asyncio.to_thread(client.generate, prompt)
        response_time_ms = max(1, round((perf_counter() - started_at) * 1000))
        scores = await asyncio.to_thread(
            self.scorer.score,
            prompt,
            client.spec.model_name,
            response_text,
        )

        return GeneratedModelResponse(
            model_name=client.spec.model_name,
            response_text=response_text,
            scores=scores,
            response_time_ms=response_time_ms,
        )
