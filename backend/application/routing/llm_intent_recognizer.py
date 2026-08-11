from __future__ import annotations

from backend.application.services.llm_service import (
    LLMService,
)

from backend.application.routing.intent_recognizer import (
    IntentRecognizer,
)

from backend.application.routing.intent_result import (
    IntentResult,
)

from backend.core.json_parser import JsonParser


class LLMIntentRecognizer(
    IntentRecognizer,
):
    """
    IntentRecognizer implementation using LLM.

    Responsibilities
    ----------------
    - Send learner message to LLM.
    - Parse JSON response.
    - Return IntentResult.
    """


    SYSTEM_PROMPT = """
You are an intent recognizer.

Your task is to identify the learner's intention.

Return ONLY JSON.

Schema:

{
    "intent": "<intent>",
    "confidence": 0.0
}


Allowed intents:

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


        result = self._parser.parse(
            raw,
        )


        return result