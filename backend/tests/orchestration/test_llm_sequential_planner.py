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