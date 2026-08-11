
from __future__ import annotations

from backend.application.runtime.runtime_context import (
    RuntimeContext,
)
from backend.core.component_context import (
    ComponentContext,
)
from backend.domain.artifact.artifact import (
    Artifact,
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
from backend.infrastructure.prompts.context_builder import (
    ContextBuilder,
)


def test_context_builder_includes_multiple_dependencies():

    workflow = Workflow()

    node = WorkflowNode(
        id="step_3",
        component_id="mentor",
        objective="Create final explanation",
        expected_output="Lesson",
    )

    workflow.add_node(
        node,
    )

    runtime = RuntimeContext(
        workflow=workflow,
    )

    research_artifact = Artifact(
        type=ArtifactType.RESEARCH,
        title="Research",
        content="Research content",
        summary="Research summary",
        producer="research",
    )

    planner_artifact = Artifact(
        type=ArtifactType.PLAN,
        title="Learning Plan",
        content="Plan content",
        summary="Plan summary",
        producer="planner",
    )

    context = ComponentContext(
        runtime=runtime,
        node=node,
        inputs={
            "research": research_artifact,
            "planner": planner_artifact,
        },
    )

    messages = ContextBuilder.build(
        context=context,
        system_prompt="You are a mentor.",
    )

    combined = "\n".join(
        message["content"]
        for message in messages
    )

    assert "Research" in combined
    assert "Research content" in combined
    assert "Research summary" in combined

    assert "Learning Plan" in combined
    assert "Plan content" in combined
    assert "Plan summary" in combined

