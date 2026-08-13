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
    - Identify one or more learner intents.
    - Parse JSON response.
    - Return IntentResult.
    """

    SYSTEM_PROMPT = """
You are an intent recognizer for an adaptive learning system.

Your task is to identify ALL meaningful learner intents
contained in the user's request.

A request may contain multiple intents.

Do not force a multi-intent request into a single intent.

Return ONLY valid JSON.

Schema:

{
    "intents": [
        {
            "intent": "<intent>",
            "confidence": 0.0
        }
    ]
}

Allowed intents:

- explain
- summarize
- compare
- roadmap
- quiz
- flashcard
- unknown

Rules:

1. Identify every meaningful intent in the request.
2. Preserve the order in which the intents appear or are logically required.
3. Do not add an intent that is not explicitly or strongly implied.
4. If the request contains multiple intents, return multiple items.
5. Confidence must be between 0.0 and 1.0.
6. If no allowed intent matches, return:
   {
       "intents": [
           {
               "intent": "unknown",
               "confidence": 1.0
           }
       ]
   }
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
            stage="routing",

        )

        return self._parser.parse(
            raw,
        )