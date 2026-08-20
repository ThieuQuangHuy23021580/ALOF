from __future__ import annotations

from backend.application.orchestration.execution_request import (
    ExecutionRequest,
)
from backend.application.orchestration.learning_orchestrator import (
    LearningOrchestrator,
)
from backend.application.planning.sequential_planner import (
    SequentialPlanner,
)
from backend.application.planning.sequential_workflow_builder import (
    SequentialWorkflowBuilder,
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
from backend.core.component_bootstrap import (
    register_components,
)
from backend.domain.learning.learning_state import (
    LearningState,
)
from backend.domain.student.student import (
    Student,
)
from backend.infrastructure.providers.groq_provider import (
    GroqProvider,
)


def test_real_llm_adaptive_learning_end_to_end():

    print("\n")
    print("=" * 70)
    print("REAL LLM END-TO-END TEST")
    print("=" * 70)

    # ==========================================================
    # Real LLM Provider
    # ==========================================================

    provider = GroqProvider()

    llm_service = LLMService(
        provider=provider,
    )

    print("\n[1] LLM PROVIDER")
    print(
        f"  - provider: "
        f"{provider.__class__.__name__}"
    )
    print(
        f"  - model: "
        f"{provider.model}"
    )

    # ==========================================================
    # Component Registry
    # ==========================================================

    register_components()

    print("\n[2] COMPONENT REGISTRY")
    print("  - Components registered successfully")

    # ==========================================================
    # Real Orchestration Pipeline
    # ==========================================================

    router = LLMRouter()

    planner = SequentialPlanner()

    workflow_builder = SequentialWorkflowBuilder()

    runtime = SequentialRuntime(
        dependencies={
            "llm": llm_service,
        },
    )

    orchestrator = LearningOrchestrator(
        router=router,
        planner=planner,
        workflow_builder=workflow_builder,
        runtime=runtime,
    )

    print("\n[3] ORCHESTRATOR")
    print("  Routing")
    print("    -> Planning")
    print("    -> Workflow Building")
    print("    -> Runtime")

    # ==========================================================
    # Student
    # ==========================================================

    student = Student(
        id="learner-1",
        display_name="Real LLM Learner",
    )

    print("\n[4] STUDENT")
    print(
        f"  - id: "
        f"{student.id}"
    )
    print(
        f"  - name: "
        f"{student.display_name}"
    )

    # ==========================================================
    # Learning State
    # ==========================================================

    learning_state = LearningState(
        learner_id="learner-1",
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

    print("\n[5] LEARNING STATE")

    print(
        "  - REST: "
        f"{learning_state.current_knowledge['rest']}"
    )

    print(
        "  - GraphQL: "
        f"{learning_state.current_knowledge['graphql']}"
    )

    print(
        "  - REST progress: "
        f"{learning_state.progress['rest']}"
    )

    print(
        "  - GraphQL progress: "
        f"{learning_state.progress['graphql']}"
    )

    print(
        "  - difficulty: "
        f"{learning_state.metadata['preferred_difficulty']}"
    )

    print(
        "  - pace: "
        f"{learning_state.metadata['preferred_pace']}"
    )

    # ==========================================================
    # Real User Request
    # ==========================================================

    message = (
        "Giải thích REST và GraphQL cho tôi, "
        "đồng thời giúp tôi hiểu khi nào nên sử dụng mỗi loại."
    )

    request = ExecutionRequest(
        student=student,
        message=message,
        learning_state=learning_state,
    )

    print("\n[6] USER REQUEST")
    print(
        f"  {message}"
    )

    # ==========================================================
    # Execute REAL END-TO-END Pipeline
    # ==========================================================

    print("\n[7] EXECUTION")
    print(
        "  Starting real LLM orchestration..."
    )

    result = orchestrator.execute(
        request,
    )

    print(
        "  Execution finished."
    )

    # ==========================================================
    # Runtime Result
    # ==========================================================

    print("\n[8] RUNTIME RESULT")

    print(
        f"  - status: "
        f"{result.status.value}"
    )

    print(
        f"  - execution order: "
        f"{result.execution_order}"
    )

    print(
        f"  - execution count: "
        f"{result.execution_count}"
    )

    print(
        f"  - artifact count: "
        f"{result.artifact_count}"
    )

    if result.duration is not None:
        print(
            f"  - duration: "
            f"{result.duration:.3f}s"
        )

    # ==========================================================
    # Artifacts
    # ==========================================================

    print("\n[9] ARTIFACTS")

    for node_id, artifact in result.artifacts.items():

        print(
            f"\n  [{node_id}]"
        )

        print(
            f"    title: "
            f"{artifact.title}"
        )

        print(
            f"    type: "
            f"{artifact.type}"
        )

        print(
            f"    producer: "
            f"{artifact.producer}"
        )

        print("    content:")

        print(
            "    "
            + artifact.content.replace(
                "\n",
                "\n    ",
            )
        )

        if artifact.summary:

            print("    summary:")

            print(
                "    "
                + artifact.summary.replace(
                    "\n",
                    "\n    ",
                )
            )

    # ==========================================================
    # Learning State
    # ==========================================================

    print("\n[10] FINAL LEARNING STATE")

    assert result.learning_state is not None

    print(
        f"  - learner_id: "
        f"{result.learning_state.learner_id}"
    )

    print(
        f"  - current knowledge: "
        f"{result.learning_state.current_knowledge}"
    )

    print(
        f"  - progress: "
        f"{result.learning_state.progress}"
    )

    # ==========================================================
    # Token Usage
    # ==========================================================

    print("\n[11] LAST LLM CALL TOKEN USAGE")

    print(
        f"  - input tokens: "
        f"{provider.last_input_tokens}"
    )

    print(
        f"  - output tokens: "
        f"{provider.last_output_tokens}"
    )

    print(
        f"  - total tokens: "
        f"{provider.last_total_tokens}"
    )

    # ==========================================================
    # Final Artifact
    # ==========================================================

    assert result.final_artifact is not None

    print("\n[12] FINAL ARTIFACT")

    print(
        f"  - producer: "
        f"{result.final_artifact.producer}"
    )

    print(
        f"  - title: "
        f"{result.final_artifact.title}"
    )

    print("\n  FINAL CONTENT:")
    print("-" * 70)

    print(
        result.final_artifact.content
    )

    print("-" * 70)

    # ==========================================================
    # Assertions
    # ==========================================================

    assert result is not None

    assert (
        result.status.value
        == "completed"
    )

    assert result.execution_order

    assert (
        result.final_artifact
        is not None
    )

    assert (
        result.final_artifact.content
    )

    assert (
        result.execution_count
        == len(result.execution_order)
    )

    assert (
        result.artifact_count
        >= 1
    )

    assert (
        result.learning_state
        is not None
    )

    assert (
        result.learning_state.learner_id
        == "learner-1"
    )

    assert (
        provider.last_total_tokens
        > 0
    )

    content = (
        result.final_artifact.content.lower()
    )

    assert "rest" in content
    assert "graphql" in content

    print("\n" + "=" * 70)
    print(
        "REAL LLM END-TO-END TEST PASSED"
    )
    print("=" * 70)