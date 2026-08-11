from __future__ import annotations

from backend.application.routing.llm_router import (
    LLMRouter,
)

from backend.application.routing.intent_result import (
    IntentResult,
)

from backend.domain.student.student import Student


class FakeIntentRecognizer:
    """
    Fake recognizer for routing test.
    """

    def recognize(
        self,
        message: str,
    ) -> IntentResult:

        return IntentResult(
            intent="compare",
            confidence=0.95,
        )


def test_llm_router():

    router = LLMRouter(
        recognizer=FakeIntentRecognizer(),
    )


    student = Student(
        display_name="Test Student",
    )


    result = router.route(
        student=student,
        message="So sánh REST và GraphQL",
    )


    assert result.intent == "compare"


    assert result.candidate_components == [
        "research",
        "mentor",
    ]


    assert result.confidence == 0.95


    assert (
        result.metadata["student_id"]
        == student.id
    )