from __future__ import annotations

from backend.application.runtime.runtime_context import (
    RuntimeContext,
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
from backend.core.component_context import (
    ComponentContext,
)
from backend.core.component_result import (
    ComponentResult,
)
from backend.core.dependency_context import (
    DependencyContext,
)
from backend.domain.artifact.artifact_type import (
    ArtifactType,
)
from backend.domain.workflow.workflow import (
    Workflow,
)
from backend.domain.workflow.workflow_node import (
    WorkflowNode,
)


# ==========================================================
# Fake LLM Provider
# ==========================================================

class FakeLLMProvider:
    """
    Fake provider for Planner -> Mentor pipeline test.
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

    return workflow


# ==========================================================
# Test
# ==========================================================

def test_planner_to_mentor_pipeline():

    llm = LLMService(
        provider=FakeLLMProvider(),
    )

    planner = PlannerComponent()
    mentor = MentorComponent()

    workflow = create_workflow()

    planner_node = workflow.nodes[0]
    mentor_node = workflow.nodes[1]

    runtime = RuntimeContext(
        workflow=workflow,
    )

    # ======================================================
    # Planner
    # ======================================================

    planner_context = ComponentContext(
        runtime=runtime,
        node=planner_node,
        dependencies=DependencyContext(
            dependencies={
                "llm": llm,
            },
        ),
    )

    planner_result = planner.invoke(
        planner_context,
    )

    # ======================================================
    # Planner assertions
    # ======================================================

    assert isinstance(
        planner_result,
        ComponentResult,
    )

    assert (
        planner_result.artifact.type
        == ArtifactType.ROADMAP
    )

    assert (
        planner_result.artifact.producer
        == "planner"
    )

    assert (
        planner_result.artifact.title
        == "Python Learning Roadmap"
    )

    # ======================================================
    # Mentor receives Planner artifact
    # ======================================================

    mentor_context = ComponentContext(
        runtime=runtime,
        node=mentor_node,
        inputs={
            "planner": planner_result.artifact,
        },
        dependencies=DependencyContext(
            dependencies={
                "llm": llm,
            },
        ),
    )

    mentor_result = mentor.invoke(
        mentor_context,
    )

    # ======================================================
    # Mentor assertions
    # ======================================================

    assert isinstance(
        mentor_result,
        ComponentResult,
    )

    assert (
        mentor_result.artifact.type
        == ArtifactType.LESSON
    )

    assert (
        mentor_result.artifact.producer
        == "mentor"
    )

    assert (
        mentor_result.artifact.title
        == "Python Lesson"
    )

    # ======================================================
    # Final validation
    # ======================================================

    assert (
        mentor_result.artifact.content
        == "Hôm nay chúng ta bắt đầu với Python cơ bản theo roadmap đã được xây dựng."
    )