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
    Fake provider for Planner -> Mentor SequentialRuntime test.
    """

    def __init__(self) -> None:

        self.responses = [
            """
            {
                "title": "Python Learning Roadmap",
                "content": "Giai đoạn 1: Python cơ bản. Giai đoạn 2: Cấu trúc dữ liệu. Giai đoạn 3: Lập trình hướng đối tượng.",
                "summary": "Roadmap học Python từ cơ bản đến nâng cao."
            }
            """,
            """
            {
                "title": "Python Lesson",
                "content": "Hôm nay chúng ta bắt đầu với Python cơ bản theo roadmap đã được xây dựng.",
                "summary": "Bài học Python cơ bản."
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

    planner_node = WorkflowNode(
        id="planner",
        component_id="planner",
        objective="Create a Python learning roadmap",
        expected_output="Roadmap",
    )

    mentor_node = WorkflowNode(
        id="mentor",
        component_id="mentor",
        objective="Create a Python lesson based on the roadmap",
        expected_output="Lesson",
    )

    workflow.add_node(
        planner_node,
    )

    workflow.add_node(
        mentor_node,
    )

    workflow.add_edge(
        WorkflowEdge(
            from_node="planner",
            to_node="mentor",
        ),
    )

    return workflow


# ==========================================================
# Test
# ==========================================================

def test_planner_to_mentor_sequential_runtime():

    # ======================================================
    # Component Registry
    # ======================================================

    ComponentRegistry.clear()

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
        "planner",
        "mentor",
    ]

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