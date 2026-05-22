from fastapi import APIRouter, Depends

from backend.app.api.deps import get_evaluation_service
from backend.app.schemas.model import AvailableModelsResponse
from backend.app.services.evaluation_service import EvaluationService


router = APIRouter(tags=["models"])


@router.get("/models", response_model=AvailableModelsResponse)
def get_models(
    service: EvaluationService = Depends(get_evaluation_service),
) -> AvailableModelsResponse:
    return AvailableModelsResponse(models=service.get_available_models())
