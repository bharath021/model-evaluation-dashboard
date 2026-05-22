from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest

from backend.app.db.repository import EvaluationRepository


class RepositorySchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = TemporaryDirectory()
        self.database_path = Path(self.tempdir.name) / "schema.sqlite3"
        self.repository = EvaluationRepository(self.database_path)
        self.repository.initialize()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_sqlite_rejects_scores_outside_the_rubric(self) -> None:
        with self.repository._connect() as connection:
            run_id = self._insert_run(connection)

            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
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
                        "gpt-4.1",
                        "Candidate output",
                        11,
                        8,
                        8,
                        25,
                        "2026-05-22T00:00:00+00:00",
                    ),
                )

    def test_deleting_a_run_cascades_to_response_rows(self) -> None:
        with self.repository._connect() as connection:
            run_id = self._insert_run(connection)
            connection.execute(
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
                    "gpt-4.1",
                    "Candidate output",
                    9,
                    8,
                    8,
                    25,
                    "2026-05-22T00:00:00+00:00",
                ),
            )

            connection.execute("DELETE FROM eval_runs WHERE id = ?", (run_id,))
            remaining = connection.execute(
                "SELECT COUNT(*) FROM model_responses"
            ).fetchone()[0]

        self.assertEqual(remaining, 0)

    @staticmethod
    def _insert_run(connection: sqlite3.Connection) -> int:
        cursor = connection.execute(
            "INSERT INTO eval_runs (prompt, created_at) VALUES (?, ?)",
            ("Prompt", "2026-05-22T00:00:00+00:00"),
        )
        return int(cursor.lastrowid)


if __name__ == "__main__":
    unittest.main()
