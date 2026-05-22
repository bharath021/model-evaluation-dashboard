from fastapi import Request

from backend.app.services.evaluation_service import EvaluationService


def get_evaluation_service(request: Request) -> EvaluationService:
    return request.app.state.evaluation_service
