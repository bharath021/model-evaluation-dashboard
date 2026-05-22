from pydantic import BaseModel

from backend.app.schemas.eval import EvalRunResponse


class EvalHistoryResponse(BaseModel):
    runs: list[EvalRunResponse]
