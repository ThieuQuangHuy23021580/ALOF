from __future__ import annotations

import pytest

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
# Fake failing component
# ==========================================================


class FailingComponent(Component):

    component_id = "failing"

    name = "Failing Component"

    description = (
        "Component used to test runtime failure handling."
    )

    def execute(
        self,
        context: ComponentContext,
    ) -> ComponentResult:

        raise RuntimeError(
            "Intentional component failure.",
        )


# ==========================================================
# Test
# ==========================================================


def test_sequential_runtime_handles_component_failure():

    # ======================================================
    # Registry
    # ======================================================

    ComponentRegistry.clear()

    ComponentRegistry.register(
        FailingComponent,
    )

    # ======================================================
    # Workflow
    # ======================================================

    workflow = Workflow()

    workflow.add_node(
        WorkflowNode(
            id="step_1",
            component_id="failing",
            objective="Trigger a component failure.",
            expected_output="Response",
        )
    )

    # ======================================================
    # Runtime Context
    # ======================================================

    context = RuntimeContext(
        workflow=workflow,
    )

    # ======================================================
    # Runtime
    # ======================================================

    runtime = SequentialRuntime()

    # ======================================================
    # Execute
    # ======================================================

    with pytest.raises(
        RuntimeError,
        match="Intentional component failure.",
    ):
        runtime.run(
            context,
        )

    # ======================================================
    # Runtime State
    # ======================================================

    assert (
        context.state.value
        == "failed"
    )

    # ======================================================
    # Error Metadata
    # ======================================================

    assert (
        context.get_metadata(
            "error",
        )
        == "Intentional component failure."
    )

    # ======================================================
    # Execution Record
    # ======================================================

    execution = (
        context.component_executions.get(
            "step_1",
        )
    )

    assert execution is not None

    assert (
        execution.status.value
        == "failed"
    )

    assert (
        execution.error
        == "Intentional component failure."
    )

    assert (
        execution.started_at
        is not None
    )

    assert (
        execution.finished_at
        is not None
    )

    # ======================================================
    # Artifact
    # ======================================================

    assert not context.has_artifact(
        "step_1",
    )

    # ======================================================
    # Execution Timeline
    # ======================================================

    assert context.execution_order == [
        "step_1",
    ]

    assert context.current_node is None

    assert context.finished_at is not None