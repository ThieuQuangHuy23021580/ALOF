from __future__ import annotations

import pytest

from backend.application.planning.llm_sequential_planner import (
    LLMSequentialPlanner,
)
from backend.application.planning.planning_request import (
    PlanningRequest,
)
from backend.application.routing.routing_result import (
    RoutingResult,
)
from backend.application.services.llm_service import (
    LLMService,
)
from backend.domain.learning.learning_state import (
    LearningState,
)
from backend.domain.student.student import (
    Student,
)


@pytest.mark.real_llm
def test_real_llm_sequential_planner():

    # ==========================================================
    # Student
    # ==========================================================

    student = Student(
        id="benchmark_student",
        display_name="Benchmark Student",
    )

    # ==========================================================
    # Routing result
    # ==========================================================

    routing = RoutingResult(
        intent="compare",
        confidence=0.95,
        candidate_components=[
            "research",
            "mentor",
        ],
    )

    # ==========================================================
    # Learning state
    # ==========================================================

    learning_state = LearningState(
        learner_id="benchmark_student",
        current_knowledge={
            "rest": "intermediate",
            "graphql": "basic",
        },
        progress={
            "rest": 0.7,
            "graphql": 0.4,
        },
        metadata={
            "preferred_difficulty": "medium",
            "preferred_pace": "normal",
        },
    )

    # ==========================================================
    # Planning request
    # ==========================================================

    request = PlanningRequest(
        student=student,
        message=(
            "Phân tích REST và GraphQL, "
            "sau đó giải thích nên sử dụng công nghệ nào "
            "trong từng trường hợp."
        ),
        routing=routing,
        learning_state=learning_state,
    )

    # ==========================================================
    # Real LLM
    # ==========================================================

    llm = LLMService()

    planner = LLMSequentialPlanner(
        llm=llm,
    )

    llm.reset_call_count()

    # ==========================================================
    # Execute planning
    # ==========================================================

    plan = planner.plan(
        request,
    )

    llm_calls = llm.call_count

    # ==========================================================
    # Assertions
    # ==========================================================

    assert plan is not None

    assert plan.steps

    assert len(plan.steps) == 2

    # ==========================================================
    # Step 1
    # ==========================================================

    first_step = plan.steps[0]

    assert first_step.id == "step_1"

    assert first_step.component == "research"

    assert first_step.objective

    assert first_step.expected_output

    assert first_step.depends_on == []

    # ==========================================================
    # Step 2
    # ==========================================================

    second_step = plan.steps[1]

    assert second_step.id == "step_2"

    assert second_step.component == "mentor"

    assert second_step.objective

    assert second_step.expected_output

    assert second_step.depends_on == [
        "step_1",
    ]

    # ==========================================================
    # LLM benchmark output
    # ==========================================================

    print(
        "\n"
        "=============================================="
    )

    print(
        "      LLM SEQUENTIAL PLANNER TEST"
    )

    print(
        "=============================================="
    )

    print(
        f"LLM calls: {llm_calls}"
    )

    print(
        f"Intent: {routing.intents}"
    )

    print(
        f"Components: "
        f"{routing.candidate_components}"
    )

    print(
        "\n--- Learning State ---"
    )

    print(
        f"Learner ID: "
        f"{learning_state.learner_id}"
    )

    print(
        f"Current Knowledge: "
        f"{learning_state.current_knowledge}"
    )

    print(
        f"Progress: "
        f"{learning_state.progress}"
    )

    print(
        f"Metadata: "
        f"{learning_state.metadata}"
    )

    print(
        "\n--- Generated Plan ---"
    )

    for step in plan.steps:

        print(
            f"\n[{step.id}]"
        )

        print(
            f"Component: {step.component}"
        )

        print(
            f"Objective: {step.objective}"
        )

        print(
            f"Expected output: "
            f"{step.expected_output}"
        )

        print(
            f"Depends on: "
            f"{step.depends_on}"
        )

    print(
        "=============================================="
    )


def test_llm_sequential_planner_includes_learning_state_in_prompt():

    # ==========================================================
    # Student
    # ==========================================================

    student = Student(
        id="learner-1",
        display_name="Test Learner",
    )

    # ==========================================================
    # Routing result
    # ==========================================================

    routing = RoutingResult(
        intent="explain",
        confidence=0.95,
        candidate_components=[
            "mentor",
        ],
    )

    # ==========================================================
    # Learning state
    # ==========================================================

    learning_state = LearningState(
        learner_id="learner-1",
        current_knowledge={
            "python": "basic",
        },
        progress={
            "python": 0.4,
        },
        metadata={
            "preferred_difficulty": "medium",
        },
    )

    # ==========================================================
    # Planning request
    # ==========================================================

    request = PlanningRequest(
        student=student,
        message="Explain Python functions.",
        routing=routing,
        learning_state=learning_state,
    )

    # ==========================================================
    # Planner
    # ==========================================================

    planner = LLMSequentialPlanner(
        llm=LLMService(),
    )

    # ==========================================================
    # Build prompt
    # ==========================================================

    prompt = planner._build_prompt(
        request,
    )

    # ==========================================================
    # Assertions
    # ==========================================================

    assert "Learner State:" in prompt

    assert "learner-1" in prompt

    # ----------------------------------------------------------
    # New LearningState structure
    # ----------------------------------------------------------

    assert "knowledge" in prompt

    assert "python" in prompt

    assert "mastery" in prompt

    assert "0.2" in prompt

    # ----------------------------------------------------------
    # Progress
    # ----------------------------------------------------------

    assert "progress" in prompt

    assert "0.4" in prompt

    # ----------------------------------------------------------
    # Metadata
    # ----------------------------------------------------------

    assert "metadata" in prompt

    assert "preferred_difficulty" in prompt

    assert "medium" in prompt