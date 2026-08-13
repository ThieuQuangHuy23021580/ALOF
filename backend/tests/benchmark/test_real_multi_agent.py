from __future__ import annotations

import pytest

from backend.application.runtime import runtime
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


def create_multi_agent_workflow() -> Workflow:
    workflow = Workflow()

    research_node = WorkflowNode(
        id="research",
        component_id="research",
        objective=(
            "Phân tích Python để cung cấp dữ liệu khách quan "
            "về khái niệm, đặc điểm chính và ứng dụng cơ bản."
        ),
        expected_output="Research",
    )

    mentor_node = WorkflowNode(
        id="mentor",
        component_id="mentor",
        objective=(
            "Giải thích Python cho người mới bắt đầu, "
            "bao gồm khái niệm, đặc điểm chính và các ứng dụng cơ bản, "
            "dựa trên kết quả nghiên cứu."
        ),
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


@pytest.mark.real_llm
def test_real_multi_agent_runtime():

    # ======================================================
    # Registry
    # ======================================================

    ComponentRegistry.clear()

    ComponentRegistry.register(
        ResearchComponent,
    )

    ComponentRegistry.register(
        MentorComponent,
    )

    # ======================================================
    # Real LLM
    # ======================================================

    llm = LLMService()

    # ======================================================
    # Workflow
    # ======================================================

    workflow = create_multi_agent_workflow()

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
    llm.reset_call_count()

    result = runtime.run(
        runtime_context,
    )

    llm_calls = llm.call_count

    # ======================================================
    # Runtime assertions
    # ======================================================

    assert result.status.value == "completed"

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

    assert research_artifact.content

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

    assert mentor_artifact.content

    # ======================================================
    # Final artifact
    # ======================================================

    assert result.final_artifact is not None

    assert (
        result.final_artifact.type
        == ArtifactType.LESSON
    )

    assert (
        result.final_artifact.producer
        == "mentor"
    )

    assert result.final_artifact.content

    # ======================================================
    # Benchmark output
    # ======================================================

    print(
        "\n"
        "=============================================="
    )

    print(
        "      REAL MULTI-AGENT BENCHMARK"
    )

    print(
        "=============================================="
    )

    print(
        f"Status: {result.status.value}"
    )

    print(
        f"Execution order: "
        f"{result.execution_order}"
    )

    print(
        f"Duration: "
        f"{result.duration:.3f}s"
        if result.duration is not None
        else "Duration: None"
    )

    print(
    f"LLM calls: {llm_calls}"
    )

    print(
        "\n--- Research Artifact ---"
    )

    print(
        research_artifact.content
    )

    print(
        "\n--- Mentor Artifact ---"
    )

    print(
        mentor_artifact.content
    )

    print(
        "\n--- Final Artifact ---"
    )

    print(
        result.final_artifact.content
    )

    print(
        "=============================================="
    )