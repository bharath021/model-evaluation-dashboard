from pydantic import BaseModel


class AvailableModel(BaseModel):
    provider: str
    model_name: str
    display_name: str
    configured: bool
    mode: str


class AvailableModelsResponse(BaseModel):
    models: list[AvailableModel]
