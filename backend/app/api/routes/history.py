from fastapi import APIRouter, Depends, Query

from backend.app.api.deps import get_evaluation_service
from backend.app.schemas.history import EvalHistoryResponse
from backend.app.services.evaluation_service import EvaluationService


router = APIRouter(tags=["history"])


@router.get("/history", response_model=EvalHistoryResponse)
def get_history(
    limit: int = Query(default=50, ge=1, le=200),
    service: EvaluationService = Depends(get_evaluation_service),
) -> EvalHistoryResponse:
    return EvalHistoryResponse(runs=service.get_history(limit=limit))
