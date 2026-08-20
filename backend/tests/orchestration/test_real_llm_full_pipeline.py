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
from backend.core.component_registry import (
    ComponentRegistry,
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


def test_real_llm_full_orchestration_pipeline():

    print("\n")
    print("=" * 70)
    print("REAL LLM FULL ORCHESTRATION E2E TEST")
    print("=" * 70)

    # ==========================================================
    # 1. LLM PROVIDER
    # ==========================================================

    provider = GroqProvider()

    llm_service = LLMService(
        provider=provider,
    )

    print("\n[1] LLM PROVIDER")
    print(
        f"  - provider: {provider.__class__.__name__}"
    )
    print(
        f"  - model: {provider.model}"
    )

    # ==========================================================
    # 2. COMPONENT BOOTSTRAP
    # ==========================================================

    print("\n[2] COMPONENT BOOTSTRAP")

    register_components()

    registered_components = (
        ComponentRegistry.ids()
    )

    print(
        f"  - registered components: "
        f"{registered_components}"
    )

    required_components = {
        "mentor",
        "research",
        "flashcard",
        "quiz",
    }

    assert required_components.issubset(
        set(registered_components)
    )

    # ==========================================================
    # 3. STUDENT
    # ==========================================================

    student = Student(
        id="learner-1",
        display_name="E2E Learner",
    )

    print("\n[3] STUDENT")
    print(
        f"  - id: {student.id}"
    )
    print(
        f"  - name: {student.display_name}"
    )

    # ==========================================================
    # 4. LEARNING STATE
    # ==========================================================

    learning_state = LearningState(
        learner_id=student.id,
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

    print("\n[4] LEARNING STATE")
    print(
        f"  - knowledge: "
        f"{learning_state.current_knowledge}"
    )
    print(
        f"  - progress: "
        f"{learning_state.progress}"
    )

    # ==========================================================
    # 5. USER REQUEST
    # ==========================================================

    message = (
        "Phân tích và so sánh REST với GraphQL, "
        "sau đó tạo flashcard và quiz giúp tôi ghi nhớ "
        "các điểm quan trọng, phù hợp với trình độ hiện tại."
    )

    print("\n[5] USER REQUEST")
    print("-" * 70)
    print(message)
    print("-" * 70)

    # ==========================================================
    # 6. APPLICATION DEPENDENCIES
    # ==========================================================

    router = LLMRouter()

    planner = SequentialPlanner()

    workflow_builder = (
        SequentialWorkflowBuilder()
    )

    runtime = SequentialRuntime(
        dependencies={
            "llm": llm_service,
        },
    )

    # ==========================================================
    # 7. LEARNING ORCHESTRATOR
    # ==========================================================

    orchestrator = LearningOrchestrator(
        router=router,
        planner=planner,
        workflow_builder=workflow_builder,
        runtime=runtime,
    )

    # ==========================================================
    # 8. EXECUTION REQUEST
    # ==========================================================

    request = ExecutionRequest(
        student=student,
        learning_state=learning_state,
        message=message,
    )

    # ==========================================================
    # 9. FULL APPLICATION EXECUTION
    # ==========================================================

    print("\n[6] ORCHESTRATOR")
    print(
        "  Starting full application orchestration..."
    )

    result = orchestrator.execute(
        request,
    )

    print(
        "  Execution finished."
    )

    # ==========================================================
    # 10. RUNTIME RESULT
    # ==========================================================

    print("\n[7] RUNTIME RESULT")

    print(
        f"  - status: {result.status}"
    )

    print(
        f"  - execution order: "
        f"{result.execution_order}"
    )

    print(
        f"  - artifact count: "
        f"{len(result.artifacts)}"
    )

    print(
        f"  - duration: "
        f"{result.duration:.3f}s"
    )

    assert (
        str(result.status)
        .lower()
        .find("completed")
        >= 0
    )

    assert result.execution_order
    assert result.artifacts
    assert result.final_artifact is not None

    # ==========================================================
    # 11. EXECUTION ORDER
    # ==========================================================

    print("\n[8] EXECUTION ORDER")

    expected_order = [
        "step_1",
        "step_2",
        "step_3",
        "step_4",
    ]

    print(
        f"  - expected: {expected_order}"
    )

    print(
        f"  - actual:   {result.execution_order}"
    )

    assert (
        result.execution_order
        == expected_order
    )

    # ==========================================================
    # 12. ARTIFACTS
    # ==========================================================

    print("\n[9] ARTIFACTS")

    producers = []

    for node_id in result.execution_order:

        artifact = result.artifacts.get(
            node_id,
        )

        assert artifact is not None
        assert artifact.title
        assert artifact.content
        assert artifact.producer

        producers.append(
            artifact.producer,
        )

        print(
            f"\n  [{node_id}]"
        )

        print(
            f"    producer: "
            f"{artifact.producer}"
        )

        print(
            f"    type: "
            f"{artifact.type}"
        )

        print(
            f"    title: "
            f"{artifact.title}"
        )

        print(
            "    content:"
        )

        print("-" * 70)
        print(artifact.content)
        print("-" * 70)

        if artifact.summary:
            print(
                f"    summary: "
                f"{artifact.summary}"
            )

    # ==========================================================
    # 13. PRODUCER VALIDATION
    # ==========================================================

    print("\n[10] PRODUCER VALIDATION")

    expected_producers = {
        "mentor",
        "research",
        "flashcard",
        "quiz",
    }

    print(
        f"  - expected: "
        f"{expected_producers}"
    )

    print(
        f"  - actual:   "
        f"{set(producers)}"
    )

    assert set(producers) == (
        expected_producers
    )

    # ==========================================================
    # 14. FINAL ARTIFACT
    # ==========================================================

    final_artifact = (
        result.final_artifact
    )

    print("\n[11] FINAL ARTIFACT")

    print(
        f"  - producer: "
        f"{final_artifact.producer}"
    )

    print(
        f"  - type: "
        f"{final_artifact.type}"
    )

    print(
        f"  - title: "
        f"{final_artifact.title}"
    )

    assert final_artifact.content
    assert final_artifact.summary

    assert (
        final_artifact.producer
        == "quiz"
    )

    # ==========================================================
    # 15. TOKEN USAGE
    # ==========================================================

    print("\n[12] LLM TOKEN USAGE")

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

    assert provider.last_total_tokens > 0

    # ==========================================================
    # 16. FINAL ASSERTIONS
    # ==========================================================

    print("\n[13] FINAL E2E ASSERTIONS")

    assert len(
        result.execution_order
    ) == 4

    assert len(
        result.artifacts
    ) == 4

    assert set(
        producers
    ) == expected_producers

    print(
        "  - Routing:       PASS"
    )

    print(
        "  - Planning:      PASS"
    )

    print(
        "  - Workflow:      PASS"
    )

    print(
        "  - Bootstrap:     PASS"
    )

    print(
        "  - Runtime:       PASS"
    )

    print(
        "  - Components:    PASS"
    )

    print(
        "  - Artifacts:     PASS"
    )

    print(
        "  - Final output:  PASS"
    )

    print(
        "  - Token usage:   PASS"
    )

    print("\n" + "=" * 70)

    print(
        "REAL LLM FULL ORCHESTRATION E2E TEST PASSED"
    )

    print("=" * 70)