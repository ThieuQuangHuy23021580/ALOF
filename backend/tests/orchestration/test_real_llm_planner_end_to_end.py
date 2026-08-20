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

from backend.components.mentor.mentor_component import (
    MentorComponent,
)
from backend.components.planner.planner_component import (
    PlannerComponent,
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


def test_real_llm_planner_agent_end_to_end():

    print("\n")
    print("=" * 70)
    print("REAL LLM PLANNER AGENT END-TO-END TEST")
    print("=" * 70)

    # ==========================================================
    # Component Registry
    # ==========================================================

    ComponentRegistry.clear()

    ComponentRegistry.register(
        MentorComponent,
    )

    ComponentRegistry.register(
        PlannerComponent,
    )

    print("\n[1] COMPONENT REGISTRY")

    print("  - mentor")
    print("  - planner")

    # ==========================================================
    # Real LLM Provider
    # ==========================================================

    provider = GroqProvider()

    llm_service = LLMService(
        provider=provider,
    )

    print("\n[2] LLM PROVIDER")

    print(
        f"  - provider: "
        f"{provider.__class__.__name__}"
    )

    print(
        f"  - model: "
        f"{provider.model}"
    )

    # ==========================================================
    # Orchestration Pipeline
    # ==========================================================

    orchestrator = LearningOrchestrator(
        router=LLMRouter(),
        planner=SequentialPlanner(),
        workflow_builder=SequentialWorkflowBuilder(),
        runtime=SequentialRuntime(
            dependencies={
                "llm": llm_service,
            },
        ),
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
        display_name="Real Planner Learner",
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
            "python": "basic",
            "algorithms": "basic",
        },
        progress={
            "python": 0.4,
            "algorithms": 0.2,
        },
        metadata={
            "preferred_difficulty": "medium",
            "preferred_pace": "normal",
        },
    )

    print("\n[5] LEARNING STATE")

    print(
        f"  - Python: "
        f"{learning_state.current_knowledge['python']}"
    )

    print(
        f"  - Algorithms: "
        f"{learning_state.current_knowledge['algorithms']}"
    )

    print(
        f"  - Python progress: "
        f"{learning_state.progress['python']}"
    )

    print(
        f"  - Algorithms progress: "
        f"{learning_state.progress['algorithms']}"
    )

    print(
        f"  - difficulty: "
        f"{learning_state.metadata['preferred_difficulty']}"
    )

    print(
        f"  - pace: "
        f"{learning_state.metadata['preferred_pace']}"
    )

    # ==========================================================
    # Real User Request
    # ==========================================================

    message = (
        "Tôi muốn học Python và thuật toán từ trình độ hiện tại. "
        "Hãy xây dựng cho tôi một lộ trình học tập có thứ tự "
        "và phù hợp với trình độ hiện tại."
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
    # Execute REAL E2E
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

        print(
            "    content:"
        )

        print(
            "    "
            + artifact.content.replace(
                "\n",
                "\n    ",
            )
        )

        if artifact.summary:

            print(
                "    summary:"
            )

            print(
                "    "
                + artifact.summary.replace(
                    "\n",
                    "\n    ",
                )
            )

    # ==========================================================
    # Token Usage
    # ==========================================================

    print("\n[10] LLM TOKEN USAGE")

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

    print("\n[11] FINAL ARTIFACT")

    print(
        f"  - producer: "
        f"{result.final_artifact.producer}"
    )

    print(
        f"  - title: "
        f"{result.final_artifact.title}"
    )

    print("\n  FINAL CONTENT:")

    print(
        "-" * 70
    )

    print(
        result.final_artifact.content
    )

    print(
        "-" * 70
    )

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
        == len(
            result.execution_order,
        )
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

    # ==========================================================
    # Planner Agent Must Execute
    # ==========================================================

    assert "planner" in [
        artifact.producer
        for artifact in result.artifacts.values()
    ]

    # ==========================================================
    # Final Content
    # ==========================================================

    content = (
        result.final_artifact.content.lower()
    )

    assert "python" in content

    assert (
        "thuật toán" in content
        or "algorithm" in content
    )

    print("\n" + "=" * 70)

    print(
        "REAL LLM PLANNER AGENT E2E TEST PASSED"
    )

    print(
        "=" * 70
    )