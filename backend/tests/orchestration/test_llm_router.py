from __future__ import annotations

import pytest

from backend.application.routing.llm_intent_recognizer import (
    LLMIntentRecognizer,
)
from backend.application.routing.llm_router import (
    LLMRouter,
)
from backend.application.services.llm_service import (
    LLMService,
)
from backend.domain.student.student import (
    Student,
)


@pytest.mark.real_llm
def test_real_llm_router():

    # ==========================================================
    # Student
    # ==========================================================

    student = Student(
        id="benchmark_student",
        display_name="Benchmark Student",
    )

    # ==========================================================
    # Learner message
    # ==========================================================

    message = (
        "Phân tích REST và GraphQL, "
        "sau đó giải thích nên sử dụng công nghệ nào "
        "trong từng trường hợp."
    )

    # ==========================================================
    # Real LLM
    # ==========================================================

    llm = LLMService()

    router = LLMRouter(
        recognizer=LLMIntentRecognizer(
            llm=llm,
        ),
    )

    llm.reset_call_count()

    # ==========================================================
    # Execute routing
    # ==========================================================

    result = router.route(
        student,
        message,
    )

    llm_calls = llm.call_count

    # ==========================================================
    # Assertions
    # ==========================================================

    assert result is not None

    # ==========================================================
    # Intents
    # ==========================================================

    assert result.intents

    assert "compare" in result.intents

    assert "explain" in result.intents

    # ==========================================================
    # Candidate components
    # ==========================================================

    assert result.candidate_components

    assert "research" in result.candidate_components

    assert "mentor" in result.candidate_components

    # ==========================================================
    # Confidence
    # ==========================================================

    assert 0.0 <= result.confidence <= 1.0

    # ==========================================================
    # Metadata
    # ==========================================================

    assert (
        result.get_metadata("student_id")
        == student.id
    )

    # ==========================================================
    # LLM
    # ==========================================================

    assert llm_calls >= 1

    # ==========================================================
    # Benchmark output
    # ==========================================================

    print(
        "\n"
        "=============================================="
    )

    print(
        "           LLM ROUTER TEST"
    )

    print(
        "=============================================="
    )

    print(
        f"LLM calls: "
        f"{llm_calls}"
    )

    print(
        f"Message: "
        f"{message}"
    )

    print(
        f"Intents: "
        f"{result.intents}"
    )

    print(
        f"Candidate components: "
        f"{result.candidate_components}"
    )

    print(
        f"Confidence: "
        f"{result.confidence}"
    )

    print(
        f"Student ID: "
        f"{result.get_metadata('student_id')}"
    )

    print(
        "=============================================="
    )