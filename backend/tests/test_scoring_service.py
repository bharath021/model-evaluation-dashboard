import unittest
from unittest.mock import patch

from backend.app.services.llm_clients.errors import LLMProviderError
from backend.app.services.scoring_service import ClaudeScorer
from backend.app.services.types import Scores


class ClaudeScorerTests(unittest.TestCase):
    @patch("backend.app.services.scoring_service.post_json")
    def test_score_requests_structured_rubric_scores(self, post_json) -> None:
        post_json.return_value = {
            "content": [
                {
                    "type": "text",
                    "text": '{"relevance": 9, "clarity": 8, "length": 7}',
                }
            ]
        }
        scorer = ClaudeScorer(api_key="test-key", model_name="claude-sonnet-4-6")

        scores = scorer.score(
            prompt="Explain HTTP caching.",
            model_name="gpt-4.1",
            response_text="HTTP caching stores reusable responses near callers.",
        )

        self.assertEqual(scores, Scores(relevance=9, clarity=8, length=7))
        payload = post_json.call_args.kwargs["payload"]
        self.assertEqual(payload["model"], "claude-sonnet-4-6")
        self.assertEqual(
            payload["output_config"]["format"]["schema"]["required"],
            ["relevance", "clarity", "length"],
        )
        self.assertIn("candidate_response", payload["messages"][0]["content"])

    @patch("backend.app.services.scoring_service.post_json")
    def test_score_rejects_out_of_range_result(self, post_json) -> None:
        post_json.return_value = {
            "content": [
                {
                    "type": "text",
                    "text": '{"relevance": 11, "clarity": 8, "length": 7}',
                }
            ]
        }
        scorer = ClaudeScorer(api_key="test-key", model_name="claude-sonnet-4-6")

        with self.assertRaisesRegex(LLMProviderError, "out-of-range relevance"):
            scorer.score(
                prompt="Explain HTTP caching.",
                model_name="gemini-2.5-flash",
                response_text="Caching stores responses for reuse.",
            )

    def test_score_requires_an_anthropic_key(self) -> None:
        scorer = ClaudeScorer(api_key=None, model_name="claude-sonnet-4-6")

        with self.assertRaisesRegex(LLMProviderError, "ANTHROPIC_API_KEY"):
            scorer.score("Prompt", "gpt-4.1", "Response")


if __name__ == "__main__":
    unittest.main()
