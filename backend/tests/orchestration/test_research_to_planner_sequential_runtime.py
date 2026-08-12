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


# ==========================================================
# Fake LLM Provider
# ==========================================================

class FakeLLMProvider:
    """
    Fake provider for Research -> Planner
    SequentialRuntime test.
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

    workflow.add_edge(
        WorkflowEdge(
            from_node="research",
            to_node="planner",
        ),
    )

    return workflow


# ==========================================================
# Test
# ==========================================================

def test_research_to_planner_sequential_runtime():

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

    assert (
        planner_artifact.content
        == (
            "Giai đoạn 1: Python cơ bản. "
            "Giai đoạn 2: Cấu trúc dữ liệu. "
            "Giai đoạn 3: Lập trình hướng đối tượng."
        )
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
        == ArtifactType.ROADMAP
    )

    assert (
        result.final_artifact.producer
        == "planner"
    )

    assert (
        result.final_artifact.title
        == "Python Learning Roadmap"
    )