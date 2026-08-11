from __future__ import annotations

from backend.application.routing.llm_intent_recognizer import (
    LLMIntentRecognizer,
)


class FakeLLMService:
    """
    Fake LLM service for testing.
    """

    def generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:

        return """
        {
            "intent": "compare",
            "confidence": 0.95
        }
        """


def test_llm_intent_recognizer():

    recognizer = LLMIntentRecognizer(
        llm=FakeLLMService(),
    )


    result = recognizer.recognize(
        "So sánh REST API và GraphQL",
    )


    assert result.intent == "compare"

    assert result.confidence == 0.95