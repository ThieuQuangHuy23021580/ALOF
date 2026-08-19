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
def test_detailed_real_end_to_end_benchmark():

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

    total_calls = llm.call_count

    total_duration = (
        llm.total_duration
    )

    total_input_tokens = (
        llm.total_input_tokens
    )

    total_output_tokens = (
        llm.total_output_tokens
    )

    total_tokens = (
        llm.total_tokens
    )

    # ==========================================================
    # Result assertions
    # ==========================================================

    assert result is not None

    assert (
        result.status.value
        == "completed"
    )

    assert result.execution_order

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
    # Stage call assertions
    # ==========================================================

    assert len(
        routing_metrics,
    ) >= 1

    assert len(
        planning_metrics,
    ) >= 1

    assert len(
        runtime_metrics,
    ) >= 1

    # ==========================================================
    # Stage token metrics
    # ==========================================================

    routing_input_tokens = (
        llm.input_tokens_by_stage(
            "routing",
        )
    )

    routing_output_tokens = (
        llm.output_tokens_by_stage(
            "routing",
        )
    )

    routing_total_tokens = (
        llm.total_tokens_by_stage(
            "routing",
        )
    )

    routing_duration = (
        llm.duration_by_stage(
            "routing",
        )
    )

    planning_input_tokens = (
        llm.input_tokens_by_stage(
            "planning",
        )
    )

    planning_output_tokens = (
        llm.output_tokens_by_stage(
            "planning",
        )
    )

    planning_total_tokens = (
        llm.total_tokens_by_stage(
            "planning",
        )
    )

    planning_duration = (
        llm.duration_by_stage(
            "planning",
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

    runtime_duration = (
        llm.duration_by_stage(
            "runtime",
        )
    )

    # ==========================================================
    # Token consistency
    # ==========================================================

    assert (
        routing_total_tokens
        == (
            routing_input_tokens
            + routing_output_tokens
        )
    )

    assert (
        planning_total_tokens
        == (
            planning_input_tokens
            + planning_output_tokens
        )
    )

    assert (
        runtime_total_tokens
        == (
            runtime_input_tokens
            + runtime_output_tokens
        )
    )

    # ==========================================================
    # E2E aggregation consistency
    # ==========================================================

    assert (
        total_input_tokens
        == (
            routing_input_tokens
            + planning_input_tokens
            + runtime_input_tokens
        )
    )

    assert (
        total_output_tokens
        == (
            routing_output_tokens
            + planning_output_tokens
            + runtime_output_tokens
        )
    )

    assert (
        total_tokens
        == (
            routing_total_tokens
            + planning_total_tokens
            + runtime_total_tokens
        )
    )

    assert (
        total_duration
        >= (
            routing_duration
            + planning_duration
            + runtime_duration
        )
    )

    # ==========================================================
    # Token sanity
    # ==========================================================

    assert total_input_tokens > 0

    assert total_output_tokens > 0

    assert total_tokens > 0

    assert total_calls >= 3

    # ==========================================================
    # Percentages
    # ==========================================================

    routing_token_percentage = (
        routing_total_tokens
        / total_tokens
        * 100
    )

    planning_token_percentage = (
        planning_total_tokens
        / total_tokens
        * 100
    )

    runtime_token_percentage = (
        runtime_total_tokens
        / total_tokens
        * 100
    )

    # ==========================================================
    # Efficiency
    # ==========================================================

    tokens_per_second = (
        total_tokens
        / total_duration
        if total_duration > 0
        else 0.0
    )

    seconds_per_call = (
        total_duration
        / total_calls
        if total_calls > 0
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
        "       ALOF E2E TOKEN BREAKDOWN BENCHMARK"
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
        f"Total duration: "
        f"{total_duration:.3f}s"
    )

    print(
        f"Total LLM calls: "
        f"{total_calls}"
    )

    print(
        f"Input tokens: "
        f"{total_input_tokens}"
    )

    print(
        f"Output tokens: "
        f"{total_output_tokens}"
    )

    print(
        f"Total tokens: "
        f"{total_tokens}"
    )

    print(
        "\n--- Routing ---"
    )

    print(
        f"Calls: "
        f"{len(routing_metrics)}"
    )

    print(
        f"Duration: "
        f"{routing_duration:.3f}s"
    )

    print(
        f"Input tokens: "
        f"{routing_input_tokens}"
    )

    print(
        f"Output tokens: "
        f"{routing_output_tokens}"
    )

    print(
        f"Total tokens: "
        f"{routing_total_tokens}"
    )

    print(
        f"Token share: "
        f"{routing_token_percentage:.2f}%"
    )

    print(
        "\n--- Planning ---"
    )

    print(
        f"Calls: "
        f"{len(planning_metrics)}"
    )

    print(
        f"Duration: "
        f"{planning_duration:.3f}s"
    )

    print(
        f"Input tokens: "
        f"{planning_input_tokens}"
    )

    print(
        f"Output tokens: "
        f"{planning_output_tokens}"
    )

    print(
        f"Total tokens: "
        f"{planning_total_tokens}"
    )

    print(
        f"Token share: "
        f"{planning_token_percentage:.2f}%"
    )

    print(
        "\n--- Runtime ---"
    )

    print(
        f"Calls: "
        f"{len(runtime_metrics)}"
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
        f"Token share: "
        f"{runtime_token_percentage:.2f}%"
    )

    print(
        "\n--- Efficiency ---"
    )

    print(
        f"Tokens / second: "
        f"{tokens_per_second:.3f}"
    )

    print(
        f"Seconds / LLM call: "
        f"{seconds_per_call:.3f}s"
    )

    print(
        "\n--- Execution ---"
    )

    print(
        f"Execution order: "
        f"{result.execution_order}"
    )

    print(
        "\n--- Token Consistency ---"
    )

    print(
        f"Routing + Planning + Runtime: "
        f"{routing_total_tokens}"
        f" + {planning_total_tokens}"
        f" + {runtime_total_tokens}"
        f" = {total_tokens}"
    )

    print(
        "======================================================"
    )

    print(
        "PASS"
    )

    print(
        "======================================================"
    )