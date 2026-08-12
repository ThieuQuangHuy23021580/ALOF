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
from backend.components.research.research_component import (
    ResearchComponent,
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


class FakeLLMProvider:
    """
    Fake provider for Research -> Planner -> Mentor pipeline.
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
                "summary": "Bài học Python cơ bản dựa trên nghiên cứu và roadmap."
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

    return workflow


def test_research_to_planner_to_mentor_pipeline():

    llm = LLMService(
        provider=FakeLLMProvider(),
    )

    research = ResearchComponent()
    planner = PlannerComponent()
    mentor = MentorComponent()

    workflow = create_workflow()

    research_node = workflow.nodes[0]
    planner_node = workflow.nodes[1]
    mentor_node = workflow.nodes[2]

    runtime = RuntimeContext(
        workflow=workflow,
    )

    # ======================================================
    # Research
    # ======================================================

    research_context = ComponentContext(
        runtime=runtime,
        node=research_node,
        dependencies=DependencyContext(
            dependencies={
                "llm": llm,
            },
        ),
    )

    research_result = research.invoke(
        research_context,
    )

    assert isinstance(
        research_result,
        ComponentResult,
    )

    assert (
        research_result.artifact.type
        == ArtifactType.RESEARCH
    )

    assert (
        research_result.artifact.producer
        == "research"
    )

    assert (
        research_result.artifact.title
        == "Python Research"
    )

    runtime.add_artifact(
        "research",
        research_result.artifact,
    )

    # ======================================================
    # Planner receives Research
    # ======================================================

    planner_context = ComponentContext(
        runtime=runtime,
        node=planner_node,
        inputs={
            "research": research_result.artifact,
        },
        dependencies=DependencyContext(
            dependencies={
                "llm": llm,
            },
        ),
    )

    planner_result = planner.invoke(
        planner_context,
    )

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

    runtime.add_artifact(
        "planner",
        planner_result.artifact,
    )

    # ======================================================
    # Mentor receives Research + Planner
    # ======================================================

    mentor_context = ComponentContext(
        runtime=runtime,
        node=mentor_node,
        inputs={
            "research": research_result.artifact,
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

    assert (
        mentor_result.artifact.content
        == (
            "Python là ngôn ngữ lập trình cấp cao, "
            "dễ đọc và phổ biến. Người học bắt đầu "
            "với cú pháp cơ bản."
        )
    )