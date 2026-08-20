from __future__ import annotations

from backend.application.runtime.runtime_context import RuntimeContext
from backend.core.component_context import ComponentContext
from backend.core.dependency_context import DependencyContext
from backend.domain.artifact.artifact import Artifact
from backend.domain.learning.learning_state import LearningState
from backend.domain.student.student import Student
from backend.domain.workflow.workflow import Workflow
from backend.domain.workflow.workflow_node import WorkflowNode


def test_artifact_is_available_to_dependent_component():
    # ==========================================================
    # Workflow
    # ==========================================================

    workflow = Workflow()

    research_node = WorkflowNode(
        id="step_1",
        component_id="research",
        objective="Research REST and GraphQL.",
        expected_output="Research Summary",
    )

    mentor_node = WorkflowNode(
        id="step_2",
        component_id="mentor",
        objective="Explain REST and GraphQL using research findings.",
        expected_output="Lesson",
        depends_on=["step_1"],
    )

    workflow.add_node(
        research_node,
    )

    workflow.add_node(
        mentor_node,
    )

    # ==========================================================
    # Runtime
    # ==========================================================

    runtime = RuntimeContext(
        workflow=workflow,
        learning_state=LearningState(
            learner_id="learner-1",
        ),
    )

    # ==========================================================
    # Research artifact
    # ==========================================================

    research_artifact = Artifact(
        title="REST vs GraphQL Research",
        type="research",
        producer="research",
        summary="Comparison of REST and GraphQL.",
        content=(
            "REST uses multiple resource endpoints. "
            "GraphQL uses a flexible query language."
        ),
    )

    runtime.add_artifact(
        "step_1",
        research_artifact,
    )

    # ==========================================================
    # Verify artifact exists in RuntimeContext
    # ==========================================================

    assert runtime.has_artifact(
        "step_1",
    )

    assert runtime.get_artifact(
        "step_1",
    ) is research_artifact

    # ==========================================================
    # Build ComponentContext for Mentor
    # ==========================================================

    mentor_inputs = {}

    for dependency_id in mentor_node.depends_on:

        artifact = runtime.get_artifact(
            dependency_id,
        )

        assert artifact is not None

        mentor_inputs[dependency_id] = artifact

    context = ComponentContext(
        runtime=runtime,
        node=mentor_node,
        inputs=mentor_inputs,
        dependencies=DependencyContext(),
    )

    # ==========================================================
    # Assertions
    # ==========================================================

    assert context.get_input(
        "step_1",
    ) is research_artifact

    assert context.inputs["step_1"].title == (
        "REST vs GraphQL Research"
    )

    assert context.inputs["step_1"].summary == (
        "Comparison of REST and GraphQL."
    )

    assert "REST uses multiple resource endpoints" in (
        context.inputs["step_1"].content
    )