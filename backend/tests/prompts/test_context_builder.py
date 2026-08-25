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
from backend.domain.learning.learning_state import (
    LearningState,
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
        type=ArtifactType.ROADMAP,
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


def test_context_builder_includes_learning_state():

    workflow = Workflow()

    node = WorkflowNode(
        id="step_1",
        component_id="mentor",
        objective="Explain Python",
        expected_output="Lesson",
    )

    workflow.add_node(
        node,
    )

    learning_state = LearningState(
        learner_id="learner-1",
    )

    learning_state.update_knowledge(
        "python",
        "basic syntax",
    )

    learning_state.update_knowledge(
        "variables",
        "understood",
    )

    learning_state.update_progress(
        "python",
        0.4,
    )

    learning_state.update_progress(
        "variables",
        0.8,
    )

    learning_state.set_metadata(
        "level",
        "beginner",
    )

    runtime = RuntimeContext(
        workflow=workflow,
        learning_state=learning_state,
    )

    context = ComponentContext(
        runtime=runtime,
        node=node,
    )

    messages = ContextBuilder.build(
        context=context,
        system_prompt="You are a mentor.",
    )

    combined = "\n".join(
        message["content"]
        for message in messages
    )

    assert "LEARNER STATE" in combined

    assert "learner-1" in combined

    assert "python" in combined
    assert "basic syntax" in combined

    assert "variables" in combined
    assert "understood" in combined

    assert "0.4" in combined
    assert "0.8" in combined

    assert "beginner" in combined


def test_context_builder_includes_default_learning_state():

    workflow = Workflow()

    node = WorkflowNode(
        id="step_1",
        component_id="mentor",
        objective="Explain Python",
        expected_output="Lesson",
    )

    workflow.add_node(
        node,
    )

    runtime = RuntimeContext(
        workflow=workflow,
    )

    context = ComponentContext(
        runtime=runtime,
        node=node,
    )

    messages = ContextBuilder.build(
        context=context,
        system_prompt="MENTOR PROMPT",
    )

    learner_state_message = next(
        message
        for message in messages
        if "LEARNER STATE" in message["content"]
    )

    assert "default" in (
        learner_state_message["content"]
    )

    assert "{}" in (
        learner_state_message["content"]
    )