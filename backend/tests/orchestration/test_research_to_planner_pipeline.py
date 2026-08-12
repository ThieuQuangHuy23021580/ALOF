from __future__ import annotations

from backend.application.runtime.runtime_context import (
    RuntimeContext,
)
from backend.application.services.llm_service import (
    LLMService,
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


# ==========================================================
# Fake LLM Provider
# ==========================================================

class FakeLLMProvider:
    """
    Fake provider for Research -> Planner pipeline test.
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
                "summary": "Roadmap học Python dựa trên kết quả nghiên cứu."
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

    planner_node = WorkflowNode(
        id="planner",
        component_id="planner",
        objective="Create a Python learning roadmap based on research",
        expected_output="Roadmap",
    )

    workflow.add_node(
        research_node,
    )

    workflow.add_node(
        planner_node,
    )

    return workflow


# ==========================================================
# Test
# ==========================================================

def test_research_to_planner_pipeline():

    # ======================================================
    # LLM
    # ======================================================

    llm = LLMService(
        provider=FakeLLMProvider(),
    )

    research = ResearchComponent()
    planner = PlannerComponent()

    # ======================================================
    # Workflow
    # ======================================================

    workflow = create_workflow()

    research_node = workflow.nodes[0]
    planner_node = workflow.nodes[1]

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

    # ======================================================
    # Research assertions
    # ======================================================

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

    # ======================================================
    # Planner receives Research artifact
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

    assert (
        planner_result.artifact.content
        == (
            "Giai đoạn 1: Python cơ bản. "
            "Giai đoạn 2: Cấu trúc dữ liệu. "
            "Giai đoạn 3: Lập trình hướng đối tượng."
        )
    )