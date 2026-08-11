from __future__ import annotations

import pytest

from backend.application.runtime.runtime_context import (
    RuntimeContext,
)
from backend.application.runtime.sequential_runtime import (
    SequentialRuntime,
)
from backend.core.component import Component
from backend.core.component_registry import (
    ComponentRegistry,
)
from backend.core.component_result import ComponentResult
from backend.domain.workflow.workflow import Workflow
from backend.domain.workflow.workflow_node import WorkflowNode


class FailingComponent(Component):

    component_id = "failing"

    name = "Failing Component"

    description = "Component that always fails."

    def execute(
        self,
        context,
    ) -> ComponentResult:

        raise RuntimeError(
            "Intentional component failure."
        )


def test_sequential_runtime_failure():

    ComponentRegistry.clear()

    ComponentRegistry.register(
        FailingComponent,
    )

    workflow = Workflow()

    workflow.add_node(
        WorkflowNode(
            id="step_1",
            component_id="failing",
            objective="Trigger failure",
            expected_output="Nothing",
        )
    )

    context = RuntimeContext(
        workflow=workflow,
    )

    runtime = SequentialRuntime()

    with pytest.raises(
        RuntimeError,
        match="Intentional component failure.",
    ):
        runtime.run(
            context,
        )

    assert context.state.value == "failed"

    assert context.metadata["error"] == (
        "Intentional component failure."
    )

    assert context.current_node is None

    assert context.finished_at is not None