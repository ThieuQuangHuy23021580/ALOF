from __future__ import annotations

from backend.application.runtime.runtime_context import (
    RuntimeContext,
)
from backend.application.runtime.sequential_runtime import (
    SequentialRuntime,
)
from backend.core.component import Component
from backend.core.component_context import ComponentContext
from backend.core.component_registry import (
    ComponentRegistry,
)
from backend.core.component_result import (
    ComponentResult,
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


# ==========================================================
# Fake Components
# ==========================================================


class FakeResearchComponent(Component):

    component_id = "research"

    name = "Fake Research"

    description = "Fake research component for runtime testing."

    def execute(
        self,
        context: ComponentContext,
    ) -> ComponentResult:

        artifact = Artifact(
            type=ArtifactType.RESEARCH,
            title="REST vs GraphQL Research",
            content=(
                "REST uses resource-based endpoints. "
                "GraphQL uses a flexible query language."
            ),
            producer=self.component_id,
        )

        return ComponentResult(
            artifact=artifact,
        )


class FakeMentorComponent(Component):

    component_id = "mentor"

    name = "Fake Mentor"

    description = "Fake mentor component for runtime testing."

    def execute(
        self,
        context: ComponentContext,
    ) -> ComponentResult:

        # ------------------------------------------------------
        # Verify artifact propagation
        # ------------------------------------------------------

        research_artifact = context.get_input(
            "step_1",
        )

        assert research_artifact is not None

        assert (
            research_artifact.content
            == (
                "REST uses resource-based endpoints. "
                "GraphQL uses a flexible query language."
            )
        )

        artifact = Artifact(
            type=ArtifactType.RESPONSE,
            title="REST vs GraphQL Lesson",
            content=(
                "Lesson based on: "
                + research_artifact.content
            ),
            producer=self.component_id,
        )

        return ComponentResult(
            artifact=artifact,
        )


# ==========================================================
# Test
# ==========================================================


def test_sequential_runtime_executes_workflow_and_propagates_artifacts():

    # ==========================================================
    # Registry
    # ==========================================================

    ComponentRegistry.clear()

    ComponentRegistry.register(
        FakeResearchComponent,
    )

    ComponentRegistry.register(
        FakeMentorComponent,
    )

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
        objective=(
            "Explain REST and GraphQL "
            "using the research findings."
        ),
        expected_output="Lesson",
        depends_on=[
            "step_1",
        ],
    )

    workflow.add_node(
        research_node,
    )

    workflow.add_node(
        mentor_node,
    )

    # ==========================================================
    # Runtime Context
    # ==========================================================

    runtime_context = RuntimeContext(
        workflow=workflow,
        learning_state=LearningState(
            learner_id="learner-1",
        ),
    )

    # ==========================================================
    # Runtime
    # ==========================================================

    runtime = SequentialRuntime()

    # ==========================================================
    # Execute
    # ==========================================================

    result = runtime.run(
        runtime_context,
    )

    # ==========================================================
    # Runtime Result
    # ==========================================================

    assert result.status.value == "completed"

    assert result.execution_order == [
        "step_1",
        "step_2",
    ]

    assert result.execution_count == 2

    assert result.artifact_count == 2

    # ==========================================================
    # Research Artifact
    # ==========================================================

    research_artifact = (
        result.artifacts.get(
            "step_1",
        )
    )

    assert research_artifact is not None

    assert (
        research_artifact.producer
        == "research"
    )

    # ==========================================================
    # Mentor Artifact
    # ==========================================================

    mentor_artifact = (
        result.artifacts.get(
            "step_2",
        )
    )

    assert mentor_artifact is not None

    assert (
        mentor_artifact.producer
        == "mentor"
    )

    assert (
        "Lesson based on:"
        in mentor_artifact.content
    )

    # ==========================================================
    # Final Artifact
    # ==========================================================

    assert result.final_artifact is not None

    assert (
        result.final_artifact.producer
        == "mentor"
    )

    # ==========================================================
    # Component Execution
    # ==========================================================

    research_execution = (
        runtime_context.component_executions.get(
            "step_1",
        )
    )

    mentor_execution = (
        runtime_context.component_executions.get(
            "step_2",
        )
    )

    assert research_execution is not None

    assert mentor_execution is not None

    assert (
        research_execution.status.value
        == "completed"
    )

    assert (
        mentor_execution.status.value
        == "completed"
    )

    assert (
        research_execution.started_at
        is not None
    )

    assert (
        research_execution.finished_at
        is not None
    )

    assert (
        mentor_execution.started_at
        is not None
    )

    assert (
        mentor_execution.finished_at
        is not None
    )