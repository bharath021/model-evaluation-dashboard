from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.api.deps import get_evaluation_service
from backend.app.schemas.eval import EvalRunRequest, EvalRunResponse
from backend.app.services.evaluation_service import EvaluationService
from backend.app.services.llm_clients.errors import LLMProviderError


router = APIRouter(tags=["evaluations"])


@router.post("/run-eval", response_model=EvalRunResponse, status_code=status.HTTP_201_CREATED)
async def run_eval(
    request: EvalRunRequest,
    service: EvaluationService = Depends(get_evaluation_service),
) -> EvalRunResponse:
    try:
        run = await service.run_evaluation(request.prompt)
    except LLMProviderError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return EvalRunResponse.model_validate(run)
