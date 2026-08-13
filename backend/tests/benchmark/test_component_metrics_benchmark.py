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
def test_real_component_metrics_benchmark():

    # ==========================================================
    # Scenario
    # ==========================================================

    scenario_name = (
        "compare_rest_graphql"
    )

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
    # Workflow builder
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
    # Basic assertions
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

    # ==========================================================
    # Component metrics
    # ==========================================================

    research_metrics = (
        llm.metrics_by_component(
            "research",
        )
    )

    mentor_metrics = (
        llm.metrics_by_component(
            "mentor",
        )
    )

    # ==========================================================
    # Component call assertions
    # ==========================================================

    assert len(
        research_metrics,
    ) >= 1

    assert len(
        mentor_metrics,
    ) >= 1

    # ==========================================================
    # Component durations
    # ==========================================================

    research_duration = (
        llm.duration_by_component(
            "research",
        )
    )

    mentor_duration = (
        llm.duration_by_component(
            "mentor",
        )
    )

    assert research_duration > 0.0

    assert mentor_duration > 0.0

    # ==========================================================
    # Component tokens
    # ==========================================================

    research_input_tokens = (
        llm.input_tokens_by_component(
            "research",
        )
    )

    research_output_tokens = (
        llm.output_tokens_by_component(
            "research",
        )
    )

    research_total_tokens = (
        llm.total_tokens_by_component(
            "research",
        )
    )

    mentor_input_tokens = (
        llm.input_tokens_by_component(
            "mentor",
        )
    )

    mentor_output_tokens = (
        llm.output_tokens_by_component(
            "mentor",
        )
    )

    mentor_total_tokens = (
        llm.total_tokens_by_component(
            "mentor",
        )
    )

    # ==========================================================
    # Token assertions
    # ==========================================================

    assert research_input_tokens >= 0

    assert research_output_tokens >= 0

    assert research_total_tokens >= 0

    assert mentor_input_tokens >= 0

    assert mentor_output_tokens >= 0

    assert mentor_total_tokens >= 0

    # ==========================================================
    # Runtime consistency
    # ==========================================================

    runtime_metrics = (
        llm.metrics_by_stage(
            "runtime",
        )
    )

    assert len(
        runtime_metrics,
    ) >= 2

    runtime_duration = (
        llm.duration_by_stage(
            "runtime",
        )
    )

    runtime_input_tokens = (
        llm.input_tokens_by_stage(
            "runtime",
        )
    )

    runtime_output_tokens = (
        llm.output_tokens_by_stage(
            "runtime",
        )
    )

    runtime_total_tokens = (
        llm.total_tokens_by_stage(
            "runtime",
        )
    )

    component_duration = (
        research_duration
        + mentor_duration
    )

    component_input_tokens = (
        research_input_tokens
        + mentor_input_tokens
    )

    component_output_tokens = (
        research_output_tokens
        + mentor_output_tokens
    )

    component_total_tokens = (
        research_total_tokens
        + mentor_total_tokens
    )

    # ==========================================================
    # Duration consistency
    # ==========================================================

    assert abs(
        runtime_duration
        - component_duration
    ) < 0.001

    # ==========================================================
    # Token consistency
    # ==========================================================

    assert (
        runtime_input_tokens
        == component_input_tokens
    )

    assert (
        runtime_output_tokens
        == component_output_tokens
    )

    assert (
        runtime_total_tokens
        == component_total_tokens
    )

    # ==========================================================
    # Total LLM consistency
    # ==========================================================

    total_calls = (
        llm.call_count
    )

    routing_calls = len(
        llm.metrics_by_stage(
            "routing",
        )
    )

    planning_calls = len(
        llm.metrics_by_stage(
            "planning",
        )
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
    # Component latency shares
    # ==========================================================

    research_latency_share = (
        research_duration
        / runtime_duration
        * 100.0
    )

    mentor_latency_share = (
        mentor_duration
        / runtime_duration
        * 100.0
    )

    # ==========================================================
    # Component token shares
    # ==========================================================

    research_token_share = (
        research_total_tokens
        / runtime_total_tokens
        * 100.0
        if runtime_total_tokens > 0
        else 0.0
    )

    mentor_token_share = (
        mentor_total_tokens
        / runtime_total_tokens
        * 100.0
        if runtime_total_tokens > 0
        else 0.0
    )

    # ==========================================================
    # Benchmark output
    # ==========================================================

    print(
        "\n"
        "======================================================"
    )

    print(
        "       ALOF COMPONENT METRICS BENCHMARK"
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
        f"Status: "
        f"{result.status.value}"
    )

    print(
        f"Total LLM calls: "
        f"{total_calls}"
    )

    print(
        "\n--- Research ---"
    )

    print(
        f"Calls: "
        f"{len(research_metrics)}"
    )

    print(
        f"Duration: "
        f"{research_duration:.3f}s"
    )

    print(
        f"Latency share: "
        f"{research_latency_share:.2f}%"
    )

    print(
        f"Input tokens: "
        f"{research_input_tokens}"
    )

    print(
        f"Output tokens: "
        f"{research_output_tokens}"
    )

    print(
        f"Total tokens: "
        f"{research_total_tokens}"
    )

    print(
        f"Token share: "
        f"{research_token_share:.2f}%"
    )

    print(
        "\n--- Mentor ---"
    )

    print(
        f"Calls: "
        f"{len(mentor_metrics)}"
    )

    print(
        f"Duration: "
        f"{mentor_duration:.3f}s"
    )

    print(
        f"Latency share: "
        f"{mentor_latency_share:.2f}%"
    )

    print(
        f"Input tokens: "
        f"{mentor_input_tokens}"
    )

    print(
        f"Output tokens: "
        f"{mentor_output_tokens}"
    )

    print(
        f"Total tokens: "
        f"{mentor_total_tokens}"
    )

    print(
        f"Token share: "
        f"{mentor_token_share:.2f}%"
    )

    print(
        "\n--- Runtime ---"
    )

    print(
        f"Calls: "
        f"{runtime_calls}"
    )

    print(
        f"Duration: "
        f"{runtime_duration:.3f}s"
    )

    print(
        f"Input tokens: "
        f"{runtime_input_tokens}"
    )

    print(
        f"Output tokens: "
        f"{runtime_output_tokens}"
    )

    print(
        f"Total tokens: "
        f"{runtime_total_tokens}"
    )

    print(
        "\n--- Consistency ---"
    )

    print(
        f"Component duration: "
        f"{component_duration:.3f}s"
    )

    print(
        f"Runtime duration: "
        f"{runtime_duration:.3f}s"
    )

    print(
        f"Component total tokens: "
        f"{component_total_tokens}"
    )

    print(
        f"Runtime total tokens: "
        f"{runtime_total_tokens}"
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