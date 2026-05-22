from dataclasses import dataclass
from pathlib import Path
import os


BACKEND_ROOT = Path(__file__).resolve().parents[2]


def _split_origins(raw_origins: str) -> list[str]:
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


@dataclass(frozen=True)
class Settings:
    app_name: str = "Model Evaluation Dashboard API"
    database_path: Path = BACKEND_ROOT / "data" / "evals.sqlite3"
    llm_mode: str = "mock"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    gemini_api_key: str | None = None
    openai_model: str = "gpt-4.1"
    anthropic_model: str = "claude-sonnet-4-6"
    anthropic_scorer_model: str = "claude-sonnet-4-6"
    gemini_model: str = "gemini-2.5-flash"
    cors_origins: tuple[str, ...] = (
        "http://localhost:5173",
        "http://localhost:3000",
    )

    @classmethod
    def from_env(cls) -> "Settings":
        database_path = Path(
            os.getenv("DATABASE_PATH", str(BACKEND_ROOT / "data" / "evals.sqlite3"))
        ).expanduser()
        llm_mode = os.getenv("LLM_MODE", "mock").strip().lower()
        cors_origins = tuple(
            _split_origins(
                os.getenv(
                    "CORS_ORIGINS",
                    "http://localhost:5173,http://localhost:3000",
                )
            )
        )

        return cls(
            database_path=database_path,
            llm_mode=llm_mode,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1"),
            anthropic_model=os.getenv(
                "ANTHROPIC_MODEL",
                "claude-sonnet-4-6",
            ),
            anthropic_scorer_model=os.getenv(
                "ANTHROPIC_SCORER_MODEL",
                "claude-sonnet-4-6",
            ),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            cors_origins=cors_origins,
        )
