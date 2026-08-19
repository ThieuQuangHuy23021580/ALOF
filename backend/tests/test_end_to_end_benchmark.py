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
from backend.benchmark.benchmark_result import BenchmarkResult
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
def test_real_end_to_end_benchmark():

    # ==========================================================
    # Scenario
    # ==========================================================

    scenario = (
        "compare_rest_graphql"
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
    # Learner request
    # ==========================================================

    message = (
        "Phân tích REST và GraphQL, "
        "sau đó giải thích nên sử dụng công nghệ nào "
        "trong từng trường hợp."
    )

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
    # Reset LLM counter
    # ==========================================================

    llm.reset_call_count()

    # ==========================================================
    # Execute
    # ==========================================================

    result = orchestrator.execute(
        request,
    )

    llm_calls = llm.call_count

    # ==========================================================
    # Assertions
    # ==========================================================

    assert result is not None

    assert result.status.value == "completed"

    assert result.execution_order

    assert result.final_artifact is not None

    assert llm_calls >= 4

    # ==========================================================
    # Extract routing information
    # ==========================================================

    # The current RuntimeResult does not expose RoutingResult.
    #
    # Therefore routing is measured independently here only
    # for benchmark metadata.
    #
    # The actual end-to-end execution has already been validated
    # by test_real_learning_orchestrator.

    benchmark_router = LLMRouter(
        recognizer=LLMIntentRecognizer(
            llm=llm,
        ),
    )

    routing = benchmark_router.route(
        student,
        message,
    )

    # ==========================================================
    # Build benchmark plan representation
    # ==========================================================

    plan_data: list[dict[str, object]] = []

    for step_id in result.execution_order:

        artifact = result.artifacts.get(
            step_id,
        )

        plan_data.append(
            {
                "id": step_id,
                "component": (
                    artifact.producer
                    if artifact is not None
                    else None
                ),
            }
        )

    # ==========================================================
    # Build artifact representation
    # ==========================================================

    artifact_data: list[dict[str, object]] = []

    for step_id, artifact in (
        result.artifacts.items()
    ):

        artifact_data.append(
            {
                "step_id": step_id,
                "type": artifact.type.value,
                "producer": artifact.producer,
                "has_content": bool(
                    artifact.content
                ),
            }
        )

    # ==========================================================
    # Final artifact representation
    # ==========================================================

    final_artifact_data = {
        "type": (
            result.final_artifact.type.value
        ),
        "producer": (
            result.final_artifact.producer
        ),
        "has_content": bool(
            result.final_artifact.content
        ),
    }

    # ==========================================================
    # Benchmark result
    # ==========================================================

    benchmark = BenchmarkResult(
        scenario=scenario,
        status=result.status.value,
        duration=result.duration,
        llm_calls=llm_calls,
        intents=routing.intents,
        candidate_components=(
            routing.candidate_components
        ),
        execution_order=(
            result.execution_order
        ),
        plan=plan_data,
        artifacts=artifact_data,
        final_artifact=final_artifact_data,
    )

    # ==========================================================
    # Benchmark assertions
    # ==========================================================

    assert benchmark.scenario == scenario

    assert benchmark.status == "completed"

    assert benchmark.duration is not None

    assert benchmark.duration >= 0.0

    assert benchmark.llm_calls >= 4

    assert benchmark.intents

    assert benchmark.candidate_components

    assert benchmark.execution_order == [
        "step_1",
        "step_2",
    ]

    assert benchmark.plan

    assert benchmark.artifacts

    assert benchmark.final_artifact is not None

    # ==========================================================
    # Benchmark output
    # ==========================================================

    print(
        "\n"
        "======================================================"
    )

    print(
        "             ALOF BENCHMARK RESULT"
    )

    print(
        "======================================================"
    )

    print(
        f"Scenario: "
        f"{benchmark.scenario}"
    )

    print(
        f"Status: "
        f"{benchmark.status}"
    )

    print(
        f"Duration: "
        f"{benchmark.duration:.3f}s"
        if benchmark.duration is not None
        else "Duration: None"
    )

    print(
        f"LLM calls: "
        f"{benchmark.llm_calls}"
    )

    print(
        f"Intents: "
        f"{benchmark.intents}"
    )

    print(
        f"Candidate components: "
        f"{benchmark.candidate_components}"
    )

    print(
        f"Execution order: "
        f"{benchmark.execution_order}"
    )

    print(
        "\n--- Plan ---"
    )

    for step in benchmark.plan:

        print(
            f"{step}"
        )

    print(
        "\n--- Artifacts ---"
    )

    for artifact in benchmark.artifacts:

        print(
            f"{artifact}"
        )

    print(
        "\n--- Final Artifact ---"
    )

    print(
        benchmark.final_artifact
    )

    print(
        "======================================================"
    )