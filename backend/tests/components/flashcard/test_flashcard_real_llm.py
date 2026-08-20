from __future__ import annotations

from backend.application.runtime.runtime_context import (
    RuntimeContext,
)
from backend.application.services.llm_service import (
    LLMService,
)
from backend.components.flashcard.flashcard_component import (
    FlashcardComponent,
)
from backend.core.component_context import (
    ComponentContext,
)
from backend.core.dependency_context import (
    DependencyContext,
)
from backend.domain.artifact.artifact_type import (
    ArtifactType,
)
from backend.domain.learning.learning_state import (
    LearningState,
)
from backend.domain.workflow.workflow import (
    Workflow,
)
from backend.domain.workflow.workflow_node import (
    WorkflowNode,
)
from backend.infrastructure.providers.groq_provider import (
    GroqProvider,
)


def test_flashcard_real_llm_generates_adaptive_flashcards():

    print("\n")
    print("=" * 70)
    print("REAL LLM FLASHCARD COMPONENT TEST")
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
    # Workflow
    # ==========================================================

    workflow = Workflow()

    node = WorkflowNode(
        id="flashcard",
        component_id="flashcard",
        objective=(
            "Tạo flashcard giúp người học ghi nhớ "
            "các khái niệm quan trọng về REST và "
            "GraphQL, phù hợp với trình độ hiện tại."
        ),
        expected_output="Flashcards",
    )

    workflow.add_node(
        node,
    )

    print("\n[2] CURRENT TASK")
    print(
        f"  - objective: "
        f"{node.objective}"
    )
    print(
        f"  - expected output: "
        f"{node.expected_output}"
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

    print("\n[3] LEARNING STATE")
    print(
        f"  - current knowledge: "
        f"{learning_state.current_knowledge}"
    )
    print(
        f"  - progress: "
        f"{learning_state.progress}"
    )
    print(
        f"  - metadata: "
        f"{learning_state.metadata}"
    )

    # ==========================================================
    # Runtime Context
    # ==========================================================

    runtime = RuntimeContext(
        workflow=workflow,
        learning_state=learning_state,
    )

    # ==========================================================
    # Component Context
    # ==========================================================

    context = ComponentContext(
        runtime=runtime,
        node=node,
        dependencies=DependencyContext(
            dependencies={
                "llm": llm_service,
            },
        ),
    )

    # ==========================================================
    # Execute Real LLM
    # ==========================================================

    component = FlashcardComponent()

    print("\n[4] EXECUTION")
    print(
        "  Starting real LLM flashcard generation..."
    )

    result = component.execute(
        context,
    )

    print(
        "  Flashcard generation finished."
    )

    # ==========================================================
    # Artifact
    # ==========================================================

    assert result is not None
    assert result.artifact is not None

    artifact = result.artifact

    print("\n[5] ARTIFACT")

    print(
        f"  - producer: "
        f"{artifact.producer}"
    )

    print(
        f"  - type: "
        f"{artifact.type}"
    )

    print(
        f"  - title: "
        f"{artifact.title}"
    )

    print("\n  CONTENT:")
    print("-" * 70)
    print(artifact.content)
    print("-" * 70)

    if artifact.summary:

        print("\n  SUMMARY:")
        print(artifact.summary)

    # ==========================================================
    # Token Usage
    # ==========================================================

    print("\n[6] LLM TOKEN USAGE")

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
    # Assertions
    # ==========================================================

    assert artifact.title
    assert artifact.content
    assert artifact.summary

    assert artifact.producer == "flashcard"

    assert (
        str(artifact.type).lower()
        .find("flashcard")
        >= 0
    )

    assert provider.last_total_tokens > 0

    content = artifact.content.lower()

    assert "rest" in content
    assert "graphql" in content

    # Flashcard should contain question/answer content.
    assert any(
        keyword in content
        for keyword in (
            "question",
            "answer",
            "câu hỏi",
            "câu trả lời",
        )
    )

    print("\n" + "=" * 70)
    print("REAL LLM FLASHCARD COMPONENT TEST PASSED")
    print("=" * 70)