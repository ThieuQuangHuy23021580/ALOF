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
from backend.components.planner.planner_component import (
    PlannerComponent,
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


class FakeLLMProvider:
    """
    Fake provider for full
    Research -> Planner -> Mentor
    SequentialRuntime E2E test.
    """

    def __init__(self) -> None:

        self.responses = [
            """
            {
                "title": "Python Research",
                "content": "Python là ngôn ngữ lập trình cấp cao, dễ đọc và được sử dụng rộng rãi.",
                "summary": "Tổng quan về Python."
            }
            """,
            """
            {
                "title": "Python Learning Roadmap",
                "content": "Giai đoạn 1: Python cơ bản. Giai đoạn 2: Cấu trúc dữ liệu. Giai đoạn 3: Lập trình hướng đối tượng.",
                "summary": "Roadmap học Python dựa trên nghiên cứu."
            }
            """,
            """
            {
                "title": "Python Lesson",
                "content": "Python là ngôn ngữ lập trình cấp cao, dễ đọc và phổ biến. Người học bắt đầu với cú pháp cơ bản.",
                "summary": "Bài học Python dựa trên nghiên cứu và roadmap."
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


def create_workflow() -> Workflow:

    workflow = Workflow()

    research_node = WorkflowNode(
        id="research",
        component_id="research",
        objective="Research Python",
        expected_output="Research",
    )

    planner_node = WorkflowNode(
        id="planner",
        component_id="planner",
        objective="Create Python learning roadmap based on research",
        expected_output="Roadmap",
    )

    mentor_node = WorkflowNode(
        id="mentor",
        component_id="mentor",
        objective="Create Python lesson based on research and roadmap",
        expected_output="Lesson",
    )

    workflow.add_node(
        research_node,
    )

    workflow.add_node(
        planner_node,
    )

    workflow.add_node(
        mentor_node,
    )

    workflow.add_edge(
        WorkflowEdge(
            from_node="research",
            to_node="planner",
        ),
    )

    workflow.add_edge(
        WorkflowEdge(
            from_node="planner",
            to_node="mentor",
        ),
    )

    workflow.add_edge(
        WorkflowEdge(
            from_node="research",
            to_node="mentor",
        ),
    )

    return workflow


def test_research_to_planner_to_mentor_sequential_runtime():

    # ======================================================
    # Component Registry
    # ======================================================

    ComponentRegistry.clear()

    ComponentRegistry.register(
        ResearchComponent,
    )

    ComponentRegistry.register(
        PlannerComponent,
    )

    ComponentRegistry.register(
        MentorComponent,
    )

    # ======================================================
    # LLM
    # ======================================================

    llm = LLMService(
        provider=FakeLLMProvider(),
    )

    # ======================================================
    # Workflow
    # ======================================================

    workflow = create_workflow()

    runtime_context = RuntimeContext(
        workflow=workflow,
    )

    # ======================================================
    # Runtime
    # ======================================================

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
        "planner",
        "mentor",
    ]

    # ======================================================
    # Artifact count
    # ======================================================

    assert len(
        result.artifacts,
    ) == 3

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

    assert (
        research_artifact.title
        == "Python Research"
    )

    # ======================================================
    # Planner artifact
    # ======================================================

    assert "planner" in result.artifacts

    planner_artifact = (
        result.artifacts["planner"]
    )

    assert (
        planner_artifact.type
        == ArtifactType.ROADMAP
    )

    assert (
        planner_artifact.producer
        == "planner"
    )

    assert (
        planner_artifact.title
        == "Python Learning Roadmap"
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

    assert (
        result.final_artifact.title
        == "Python Lesson"
    )

    # ======================================================
    # Runtime artifacts
    # ======================================================

    assert (
        runtime_context.has_artifact(
            "research",
        )
    )

    assert (
        runtime_context.has_artifact(
            "planner",
        )
    )

    assert (
        runtime_context.has_artifact(
            "mentor",
        )
    )