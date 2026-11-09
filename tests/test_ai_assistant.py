import os
import unittest
from unittest.mock import Mock, patch

import ai_assistant


@unittest.skipUnless(ai_assistant.GENAI_AVAILABLE, "google-genai is not installed")
class TravelAIAssistantTests(unittest.TestCase):
    def test_uses_current_model_and_environment_key(self):
        with patch.dict(
            os.environ,
            {"GEMINI_API_KEY": "test-key", "GEMINI_MODEL": "test-model"},
            clear=False,
        ), patch.object(ai_assistant.genai, "Client") as client:
            assistant = ai_assistant.TravelAIAssistant()

        client.assert_called_once_with(api_key="test-key")
        self.assertEqual(assistant.model_name, "test-model")
        self.assertTrue(assistant.is_ready)

    def test_sends_prompt_and_returns_response_text(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=False):
            assistant = ai_assistant.TravelAIAssistant()
        response = type("Response", (), {"text": "  Try a daily budget.  "})()
        assistant._client = type(
            "Client",
            (),
            {
                "models": type(
                    "Models",
                    (),
                    {"generate_content": lambda _self, **_kwargs: response},
                )()
            },
        )()

        result = assistant.ask("Help me budget")

        self.assertEqual(result, "Try a daily budget.")

    def test_reports_missing_key(self):
        with patch.dict(
            os.environ,
            {"GEMINI_API_KEY": "", "GOOGLE_API_KEY": ""},
            clear=False,
        ):
            assistant = ai_assistant.TravelAIAssistant(api_key="")

        self.assertFalse(assistant.is_ready)
        self.assertIn("No Gemini API key found", assistant.status_message)

    def test_explains_unsupported_access_token(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=False):
            assistant = ai_assistant.TravelAIAssistant()
        assistant._client = Mock()
        assistant._client.models.generate_content.side_effect = RuntimeError(
            "401 API key not valid ACCESS_TOKEN_TYPE_UNSUPPORTED"
        )

        result = assistant.ask("Help me budget")

        self.assertIn("OAuth/access token instead of a Gemini API key", result)
        self.assertIn("aistudio.google.com/apikey", result)


if __name__ == "__main__":
    unittest.main()
