"""AI travel assistant powered by Google Gemini.

Requires the google-genai package and a Gemini API key.
Set the environment variable GEMINI_API_KEY (or GOOGLE_API_KEY).

Usage:
    from ai_assistant import TravelAIAssistant
    assistant = TravelAIAssistant()
    reply = assistant.ask("Suggest a 3-day budget for Accra", trip=my_trip)
"""

from __future__ import annotations

import os
from typing import Optional

# Optional dependency – the rest of the app still runs without it.
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


SYSTEM_INSTRUCTION = """
You are a helpful, concise travel-budget assistant for a Currency & Travel Budget Planner app.
You help users plan trips, understand exchange rates, stay within budget, and categorise expenses.
Categories available in the app: transport, accommodation, food, activities, other.
Supported currencies: NGN, USD, EUR, GBP, CAD, GHS, KES.
Give practical, realistic advice. Prefer short bullet points when listing ideas.
If the user provides current trip data, use those numbers and do not invent different totals.
Never invent live exchange rates; remind the user that the app uses sample offline rates.
""".strip()


class TravelAIAssistant:
    """Thin wrapper around the Gemini API for travel-budget advice."""

    DEFAULT_MODEL = "gemini-3.8-flash"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.model_name = model or os.environ.get("GEMINI_MODEL") or self.DEFAULT_MODEL
        self._client = None
        self._error = None

        if not GENAI_AVAILABLE:
            self._error = (
                "The google-genai package is not installed.\n"
                "Install it with:  pip install google-genai"
            )
            return

        key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        key = key.strip() if key else None
        if not key:
            self._error = (
                "No Gemini API key found.\n"
                "Set the environment variable GEMINI_API_KEY (or GOOGLE_API_KEY)\n"
                "or pass api_key=... when creating TravelAIAssistant."
            )
            return

        try:
            self._client = genai.Client(api_key=key)
        except Exception as exc:  # noqa: BLE001
            self._error = f"Could not initialise Gemini client: {exc}"

    @property
    def is_ready(self) -> bool:
        return self._client is not None and self._error is None

    @property
    def status_message(self) -> str:
        if self.is_ready:
            return f"Connected to Gemini ({self.model_name})"
        return self._error or "AI assistant not configured."

    def _build_trip_context(self, trip) -> str:
        """Turn a TravelBudget instance into a short text context for the model."""
        if trip is None:
            return "No active trip is loaded."

        lines = [
            f"Current trip: {trip.name}",
            f"Currency: {trip.currency}",
            f"Total budget: {trip.total_budget:,.2f} {trip.currency}",
            f"Spent so far: {trip.total_spent:,.2f} {trip.currency}",
            f"Remaining: {trip.remaining:,.2f} {trip.currency}",
            f"Status: {'Over budget' if trip.is_over_budget else 'Within budget'}",
        ]
        if trip.expenses:
            lines.append("Expenses:")
            for item in trip.expenses[-15:]:  # last 15 to keep context short
                lines.append(
                    f"  - {item['date']} | {item['category']} | "
                    f"{item['description']} | {item['amount']:,.2f} {trip.currency}"
                )
            if len(trip.expenses) > 15:
                lines.append(f"  … and {len(trip.expenses) - 15} older expenses")
        else:
            lines.append("No expenses recorded yet.")
        return "\n".join(lines)

    def ask(self, user_message: str, trip=None) -> str:
        """Send a message (plus optional trip context) to Gemini and return the reply text."""
        if not self.is_ready:
            return self.status_message

        if not user_message or not user_message.strip():
            return "Please type a question or request."

        try:
            trip_context = self._build_trip_context(trip)
            full_prompt = (
                f"{SYSTEM_INSTRUCTION}\n\n"
                f"--- Current trip data ---\n{trip_context}\n\n"
                f"--- User message ---\n{user_message.strip()}"
            )
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
            )
            text = getattr(response, "text", None)
            if text:
                return text.strip()
            return "Gemini returned an empty response. Please try asking in a different way."
        except Exception as exc:  # noqa: BLE001
            error_details = str(exc)
            if "ACCESS_TOKEN_TYPE_UNSUPPORTED" in error_details or (
                "401" in error_details and "API key not valid" in error_details
            ):
                return (
                    "Gemini rejected the configured credential. It appears to be invalid "
                    "or an OAuth/access token instead of a Gemini API key. Create an API "
                    "key in Google AI Studio (https://aistudio.google.com/apikey), then "
                    "set GEMINI_API_KEY to that key and restart the app. Do not use an "
                    "OAuth access token or service-account token."
                )
            return f"Gemini request failed ({type(exc).__name__}): {exc}"


# Convenience singleton used by the GUI (lazy-initialised)
_assistant_instance: Optional[TravelAIAssistant] = None


def get_assistant() -> TravelAIAssistant:
    global _assistant_instance
    if _assistant_instance is None:
        _assistant_instance = TravelAIAssistant()
    return _assistant_instance
