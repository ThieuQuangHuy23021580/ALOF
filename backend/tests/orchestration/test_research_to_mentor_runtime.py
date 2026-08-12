from __future__ import annotations

from backend.application.runtime.runtime_context import (
    RuntimeContext,
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
from backend.domain.artifact.artifact_type import (
    ArtifactType,
)
from backend.domain.workflow.workflow import (
    Workflow,
)
from backend.domain.workflow.workflow_edge import (
    WorkflowEdge,
)
from backend.domain.workflow.workflow_node import (
    WorkflowNode,
)


# ==========================================================
# Fake LLM Provider
# ==========================================================

class FakeLLMProvider:
    """
    Fake provider for Research -> Mentor runtime test.
    """

    def __init__(self) -> None:

        self.responses = [
            """
            {
                "title": "Python Research",
                "content": "Python là ngôn ngữ lập trình cấp cao, được sử dụng rộng rãi.",
                "summary": "Tổng quan về Python."
            }
            """,
            """
            {
                "title": "Python Lesson",
                "content": "Python là ngôn ngữ lập trình cấp cao, dễ đọc và phổ biến.",
                "summary": "Bài học giới thiệu Python."
            }
            """,
        ]

    def generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:

        assert self.responses, (
            "FakeLLMProvider received more calls "
            "than expected."
        )

        return self.responses.pop(0)


# ==========================================================
# Workflow
# ==========================================================

def create_workflow() -> Workflow:

    workflow = Workflow()

    research_node = WorkflowNode(
        id="research",
        component_id="research",
        objective="Research Python",
        expected_output="Research",
    )

    mentor_node = WorkflowNode(
        id="mentor",
        component_id="mentor",
        objective="Explain Python based on research",
        expected_output="Lesson",
    )

    workflow.add_node(
        research_node,
    )

    workflow.add_node(
        mentor_node,
    )

    workflow.add_edge(
        WorkflowEdge(
            from_node="research",
            to_node="mentor",
        ),
    )

    return workflow


# ==========================================================
# Test
# ==========================================================

def test_research_to_mentor_sequential_runtime():

    ComponentRegistry.clear()

    ComponentRegistry.register(
        ResearchComponent,
    )

    ComponentRegistry.register(
        MentorComponent,
    )

    llm = LLMService(
        provider=FakeLLMProvider(),
    )

    workflow = create_workflow()

    runtime_context = RuntimeContext(
        workflow=workflow,
    )

    runtime = SequentialRuntime(
        dependencies={
            "llm": llm,
        },
    )

    result = runtime.run(
        runtime_context,
    )

    # ======================================================
    # Runtime status
    # ======================================================

    assert result.status.value == "completed"

    # ======================================================
    # Execution order
    # ======================================================

    assert result.execution_order == [
        "research",
        "mentor",
    ]

    # ======================================================
    # Research artifact
    # ======================================================

    assert "research" in result.artifacts

    research_artifact = (
        result.artifacts["research"]
    )

    assert (
        research_artifact.type
        == ArtifactType.RESEARCH
    )

    assert (
        research_artifact.producer
        == "research"
    )

    # ======================================================
    # Mentor artifact
    # ======================================================

    assert "mentor" in result.artifacts

    mentor_artifact = (
        result.artifacts["mentor"]
    )

    assert (
        mentor_artifact.type
        == ArtifactType.LESSON
    )

    assert (
        mentor_artifact.producer
        == "mentor"
    )

    assert (
        mentor_artifact.title
        == "Python Lesson"
    )

    # ======================================================
    # Final artifact
    # ======================================================

    assert (
        result.final_artifact
        is not None
    )

    assert (
        result.final_artifact.type
        == ArtifactType.LESSON
    )

    assert (
        result.final_artifact.producer
        == "mentor"
    )