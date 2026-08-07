from __future__ import annotations

from backend.application.routing.intent_recognizer import (
    IntentRecognizer,
)
from backend.application.routing.intent_result import (
    IntentResult,
)
from backend.application.services.llm_service import LLMService
from backend.core.json_parser import JsonParser


class LLMIntentRecognizer(IntentRecognizer):
    """
    IntentRecognizer implementation based on an LLM.

    Responsibilities
    ----------------
    - Ask the LLM to identify the learner's intent.
    - Parse the JSON response into an IntentResult.
    """

    SYSTEM_PROMPT = """
You are an intent recognizer.

Return ONLY one JSON object.

Schema

{
    "intent": "<intent>",
    "confidence": 0.0
}

Allowed intents

- explain
- summarize
- compare
- roadmap
- quiz
- flashcard
- unknown
""".strip()

    def __init__(
        self,
        llm: LLMService | None = None,
    ) -> None:

        self._llm = (
            llm
            if llm is not None
            else LLMService()
        )

        self._parser = JsonParser(
            IntentResult,
        )

    def recognize(
        self,
        message: str,
    ) -> IntentResult:

        messages = [
            {
                "role": "system",
                "content": self.SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": message,
            },
        ]

        raw = self._llm.generate(
            messages,
        )

        return self._parser.parse(
            raw,
        )