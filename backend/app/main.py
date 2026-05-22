from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import evals, history, models
from backend.app.core.config import Settings
from backend.app.db.repository import EvaluationRepository
from backend.app.services.evaluation_service import EvaluationService
from backend.app.services.llm_clients.factory import build_clients
from backend.app.services.scoring_service import build_scorer


def create_app(settings: Settings | None = None) -> FastAPI:
    active_settings = settings or Settings.from_env()
    repository = EvaluationRepository(active_settings.database_path)
    repository.initialize()

    app = FastAPI(
        title=active_settings.app_name,
        version="0.1.0",
        description="Compare model responses for the same evaluation prompt.",
    )
    app.state.settings = active_settings
    app.state.evaluation_service = EvaluationService(
        repository=repository,
        clients=build_clients(active_settings),
        scorer=build_scorer(active_settings),
        llm_mode=active_settings.llm_mode,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=active_settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(evals.router)
    app.include_router(history.router)
    app.include_router(models.router)

    @app.get("/health", tags=["health"])
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
