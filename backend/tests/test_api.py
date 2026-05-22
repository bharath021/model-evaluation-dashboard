import asyncio
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from urllib.parse import urlsplit

from backend.app.core.config import Settings
from backend.app.main import create_app


class BackendApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = TemporaryDirectory()
        database_path = Path(self.tempdir.name) / "test-evals.sqlite3"
        self.app = create_app(
            Settings(
                database_path=database_path,
                llm_mode="mock",
                cors_origins=("http://localhost:5173",),
            )
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_models_lists_all_configured_clients(self) -> None:
        status_code, payload = request_json(self.app, "GET", "/models")

        self.assertEqual(status_code, 200)
        self.assertEqual(len(payload["models"]), 3)
        self.assertEqual(
            [model["provider"] for model in payload["models"]],
            ["openai", "anthropic", "google"],
        )
        self.assertTrue(all(model["configured"] for model in payload["models"]))

    def test_run_eval_persists_history(self) -> None:
        prompt = "Explain why regression tests matter in software delivery."
        status_code, run_payload = request_json(
            self.app,
            "POST",
            "/run-eval",
            {"prompt": prompt},
        )

        self.assertEqual(status_code, 201)
        self.assertEqual(run_payload["prompt"], prompt)
        self.assertEqual(len(run_payload["responses"]), 3)
        self.assertTrue(
            all(response["response_time_ms"] >= 1 for response in run_payload["responses"])
        )
        self.assertTrue(
            all(
                0 <= response["scores"]["relevance"] <= 10
                for response in run_payload["responses"]
            )
        )

        history_status, history_payload = request_json(self.app, "GET", "/history")

        self.assertEqual(history_status, 200)
        self.assertEqual(len(history_payload["runs"]), 1)
        self.assertEqual(history_payload["runs"][0]["id"], run_payload["id"])
        self.assertEqual(len(history_payload["runs"][0]["responses"]), 3)


def request_json(
    app,
    method: str,
    url: str,
    payload: dict[str, str] | None = None,
) -> tuple[int, dict]:
    return asyncio.run(_request_json(app, method, url, payload))


async def _request_json(
    app,
    method: str,
    url: str,
    payload: dict[str, str] | None,
) -> tuple[int, dict]:
    parsed_url = urlsplit(url)
    body = json.dumps(payload).encode("utf-8") if payload is not None else b""
    incoming_messages = [
        {
            "type": "http.request",
            "body": body,
            "more_body": False,
        }
    ]
    outgoing_messages = []

    async def receive() -> dict:
        if incoming_messages:
            return incoming_messages.pop(0)
        return {"type": "http.disconnect"}

    async def send(message: dict) -> None:
        outgoing_messages.append(message)

    headers = [(b"accept", b"application/json")]
    if payload is not None:
        headers.append((b"content-type", b"application/json"))

    await app(
        {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": method,
            "scheme": "http",
            "path": parsed_url.path,
            "raw_path": parsed_url.path.encode("ascii"),
            "query_string": parsed_url.query.encode("ascii"),
            "headers": headers,
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
        },
        receive,
        send,
    )

    response_start = next(
        message
        for message in outgoing_messages
        if message["type"] == "http.response.start"
    )
    response_body = b"".join(
        message.get("body", b"")
        for message in outgoing_messages
        if message["type"] == "http.response.body"
    )

    return response_start["status"], json.loads(response_body.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
