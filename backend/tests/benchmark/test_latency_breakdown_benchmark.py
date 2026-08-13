from __future__ import annotations

import pytest

from backend.application.orchestration.execution_request import (
    ExecutionRequest,
)
from backend.application.orchestration.learning_orchestrator import (
    LearningOrchestrator,
)
from backend.application.planning.llm_sequential_planner import (
    LLMSequentialPlanner,
)
from backend.application.planning.sequential_workflow_builder import (
    SequentialWorkflowBuilder,
)
from backend.application.routing.llm_intent_recognizer import (
    LLMIntentRecognizer,
)
from backend.application.routing.llm_router import (
    LLMRouter,
)
from backend.application.runtime.sequential_runtime import (
    SequentialRuntime,
)
from backend.application.services.llm_service import (
    LLMService,
)
from backend.components.mentor.mentor_component import (
    MentorComponent,
)
from backend.components.research.research_component import (
    ResearchComponent,
)
from backend.core.component_registry import (
    ComponentRegistry,
)
from backend.domain.student.student import (
    Student,
)


@pytest.mark.real_llm
def test_real_latency_breakdown_benchmark():

    # ==========================================================
    # Scenario
    # ==========================================================

    scenario_name = "compare_rest_graphql"

    message = (
        "Phân tích REST và GraphQL, "
        "sau đó giải thích nên sử dụng công nghệ nào "
        "trong từng trường hợp."
    )

    # ==========================================================
    # Registry
    # ==========================================================

    ComponentRegistry.clear()

    ComponentRegistry.register(
        ResearchComponent,
    )

    ComponentRegistry.register(
        MentorComponent,
    )

    # ==========================================================
    # Student
    # ==========================================================

    student = Student(
        id="benchmark_student",
        display_name="Benchmark Student",
    )

    # ==========================================================
    # Request
    # ==========================================================

    request = ExecutionRequest(
        student=student,
        message=message,
    )

    # ==========================================================
    # Shared LLM service
    # ==========================================================

    llm = LLMService()

    # ==========================================================
    # Router
    # ==========================================================

    router = LLMRouter(
        recognizer=LLMIntentRecognizer(
            llm=llm,
        ),
    )

    # ==========================================================
    # Planner
    # ==========================================================

    planner = LLMSequentialPlanner(
        llm=llm,
    )

    # ==========================================================
    # Workflow
    # ==========================================================

    workflow_builder = (
        SequentialWorkflowBuilder()
    )

    # ==========================================================
    # Runtime
    # ==========================================================

    runtime = SequentialRuntime(
        dependencies={
            "llm": llm,
        },
    )

    # ==========================================================
    # Orchestrator
    # ==========================================================

    orchestrator = LearningOrchestrator(
        router=router,
        planner=planner,
        workflow_builder=workflow_builder,
        runtime=runtime,
    )

    # ==========================================================
    # Reset metrics
    # ==========================================================

    llm.reset_call_count()

    # ==========================================================
    # Execute
    # ==========================================================

    result = orchestrator.execute(
        request,
    )

    # ==========================================================
    # Overall metrics
    # ==========================================================

    total_wall_clock = sum(
        metric.duration
        for metric in llm.call_metrics
    )

    total_llm_duration = (
        llm.total_duration
    )

    # ==========================================================
    # Stage metrics
    # ==========================================================

    routing_metrics = (
        llm.metrics_by_stage(
            "routing",
        )
    )

    planning_metrics = (
        llm.metrics_by_stage(
            "planning",
        )
    )

    runtime_metrics = (
        llm.metrics_by_stage(
            "runtime",
        )
    )

    # ==========================================================
    # Stage latency
    # ==========================================================

    routing_latency = sum(
        metric.duration
        for metric in routing_metrics
    )

    planning_latency = sum(
        metric.duration
        for metric in planning_metrics
    )

    runtime_latency = sum(
        metric.duration
        for metric in runtime_metrics
    )

    # ==========================================================
    # Workflow latency
    #
    # Workflow construction is currently synchronous and does
    # not make an LLM call. Therefore it is measured as zero
    # at the LLM instrumentation level.
    # ==========================================================

    workflow_latency = 0.0

    # ==========================================================
    # Assertions
    # ==========================================================

    assert result is not None

    assert (
        result.status.value
        == "completed"
    )

    assert result.execution_order == [
        "step_1",
        "step_2",
    ]

    assert len(
        routing_metrics,
    ) >= 1

    assert len(
        planning_metrics,
    ) >= 1

    assert len(
        runtime_metrics,
    ) >= 1

    assert routing_latency > 0.0

    assert planning_latency > 0.0

    assert runtime_latency > 0.0

    assert total_llm_duration > 0.0

    # ==========================================================
    # Latency consistency
    # ==========================================================

    stage_latency_sum = (
        routing_latency
        + planning_latency
        + runtime_latency
    )

    assert (
        abs(
            stage_latency_sum
            - total_llm_duration
        )
        < 0.001
    )

    # ==========================================================
    # Stage shares
    # ==========================================================

    routing_share = (
        routing_latency
        / total_llm_duration
        * 100.0
    )

    planning_share = (
        planning_latency
        / total_llm_duration
        * 100.0
    )

    runtime_share = (
        runtime_latency
        / total_llm_duration
        * 100.0
    )

    # ==========================================================
    # LLM call count
    # ==========================================================

    total_calls = llm.call_count

    routing_calls = len(
        routing_metrics,
    )

    planning_calls = len(
        planning_metrics,
    )

    runtime_calls = len(
        runtime_metrics,
    )

    assert (
        routing_calls
        + planning_calls
        + runtime_calls
        == total_calls
    )

    # ==========================================================
    # Benchmark output
    # ==========================================================

    print(
        "\n"
        "======================================================"
    )

    print(
        "        ALOF LATENCY BREAKDOWN BENCHMARK"
    )

    print(
        "======================================================"
    )

    print(
        "\n--- Scenario ---"
    )

    print(
        f"Name: {scenario_name}"
    )

    print(
        f"Message: {message}"
    )

    print(
        "\n--- Overall ---"
    )

    print(
        f"Status: {result.status.value}"
    )

    print(
        f"Total wall-clock LLM duration: "
        f"{total_wall_clock:.3f}s"
    )

    print(
        f"Total LLM duration: "
        f"{total_llm_duration:.3f}s"
    )

    print(
        f"Total LLM calls: "
        f"{total_calls}"
    )

    print(
        "\n--- Routing ---"
    )

    print(
        f"Calls: {routing_calls}"
    )

    print(
        f"Duration: "
        f"{routing_latency:.3f}s"
    )

    print(
        f"Share: "
        f"{routing_share:.2f}%"
    )

    print(
        "\n--- Planning ---"
    )

    print(
        f"Calls: {planning_calls}"
    )

    print(
        f"Duration: "
        f"{planning_latency:.3f}s"
    )

    print(
        f"Share: "
        f"{planning_share:.2f}%"
    )

    print(
        "\n--- Workflow ---"
    )

    print(
        f"Duration: "
        f"{workflow_latency:.3f}s"
    )

    print(
        "LLM calls: 0"
    )

    print(
        "\n--- Runtime ---"
    )

    print(
        f"Calls: {runtime_calls}"
    )

    print(
        f"Duration: "
        f"{runtime_latency:.3f}s"
    )

    print(
        f"Share: "
        f"{runtime_share:.2f}%"
    )

    print(
        "\n--- Latency Composition ---"
    )

    print(
        f"Routing + Planning + Runtime: "
        f"{stage_latency_sum:.3f}s"
    )

    print(
        f"Measured LLM duration: "
        f"{total_llm_duration:.3f}s"
    )

    print(
        "\n--- Execution ---"
    )

    print(
        f"Execution order: "
        f"{result.execution_order}"
    )

    print(
        "\n--- Benchmark Verdict ---"
    )

    print(
        "PASS"
    )

    print(
        "======================================================"
    )