from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from typing import Any

from backend.app.services.types import GeneratedModelResponse


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS eval_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS model_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES eval_runs(id) ON DELETE CASCADE,
    model_name TEXT NOT NULL,
    response_text TEXT NOT NULL,
    score_relevance INTEGER NOT NULL CHECK (score_relevance BETWEEN 0 AND 10),
    score_clarity INTEGER NOT NULL CHECK (score_clarity BETWEEN 0 AND 10),
    score_length INTEGER NOT NULL CHECK (score_length BETWEEN 0 AND 10),
    response_time_ms INTEGER NOT NULL CHECK (response_time_ms >= 0),
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_eval_runs_created_at
ON eval_runs(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_model_responses_run_id
ON model_responses(run_id);

CREATE INDEX IF NOT EXISTS idx_model_responses_model_created_at
ON model_responses(model_name, created_at DESC);
"""


class EvaluationRepository:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(SCHEMA_SQL)

    def create_run(
        self,
        prompt: str,
        responses: Sequence[GeneratedModelResponse],
    ) -> dict[str, Any]:
        created_at = _utc_now()
        with self._connect() as connection:
            run_cursor = connection.execute(
                "INSERT INTO eval_runs (prompt, created_at) VALUES (?, ?)",
                (prompt, created_at),
            )
            run_id = int(run_cursor.lastrowid)

            response_rows = []
            for response in responses:
                response_created_at = _utc_now()
                response_cursor = connection.execute(
                    """
                    INSERT INTO model_responses (
                        run_id,
                        model_name,
                        response_text,
                        score_relevance,
                        score_clarity,
                        score_length,
                        response_time_ms,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        response.model_name,
                        response.response_text,
                        response.scores.relevance,
                        response.scores.clarity,
                        response.scores.length,
                        response.response_time_ms,
                        response_created_at,
                    ),
                )
                response_rows.append(
                    {
                        "id": int(response_cursor.lastrowid),
                        "model_name": response.model_name,
                        "response_text": response.response_text,
                        "scores": {
                            "relevance": response.scores.relevance,
                            "clarity": response.scores.clarity,
                            "length": response.scores.length,
                        },
                        "response_time_ms": response.response_time_ms,
                        "created_at": response_created_at,
                    }
                )

        return {
            "id": run_id,
            "prompt": prompt,
            "created_at": created_at,
            "responses": response_rows,
        }

    def list_runs(self, limit: int) -> list[dict[str, Any]]:
        with self._connect() as connection:
            run_rows = connection.execute(
                """
                SELECT id, prompt, created_at
                FROM eval_runs
                ORDER BY created_at DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

            runs = []
            for run_row in run_rows:
                response_rows = connection.execute(
                    """
                    SELECT
                        id,
                        model_name,
                        response_text,
                        score_relevance,
                        score_clarity,
                        score_length,
                        response_time_ms,
                        created_at
                    FROM model_responses
                    WHERE run_id = ?
                    ORDER BY id ASC
                    """,
                    (run_row["id"],),
                ).fetchall()
                runs.append(
                    {
                        "id": run_row["id"],
                        "prompt": run_row["prompt"],
                        "created_at": run_row["created_at"],
                        "responses": [
                            {
                                "id": response_row["id"],
                                "model_name": response_row["model_name"],
                                "response_text": response_row["response_text"],
                                "scores": {
                                    "relevance": response_row["score_relevance"],
                                    "clarity": response_row["score_clarity"],
                                    "length": response_row["score_length"],
                                },
                                "response_time_ms": response_row["response_time_ms"],
                                "created_at": response_row["created_at"],
                            }
                            for response_row in response_rows
                        ],
                    }
                )

        return runs

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
