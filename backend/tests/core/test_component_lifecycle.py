from __future__ import annotations

from backend.application.runtime.runtime_context import (
    RuntimeContext,
)
from backend.core.component import Component
from backend.core.component_context import ComponentContext
from backend.core.component_result import ComponentResult
from backend.domain.artifact.artifact import Artifact
from backend.domain.artifact.artifact_type import ArtifactType
from backend.domain.workflow.workflow import Workflow
from backend.domain.workflow.workflow_node import WorkflowNode


class LifecycleComponent(Component):

    component_id = "lifecycle_test"

    name = "Lifecycle Test"

    description = "Test component lifecycle."

    def __init__(
        self,
    ) -> None:

        self.events: list[str] = []

    def before_execute(
        self,
        context: ComponentContext,
    ) -> None:

        self.events.append(
            "before",
        )

    def execute(
        self,
        context: ComponentContext,
    ) -> ComponentResult:

        self.events.append(
            "execute",
        )

        artifact = Artifact(
            type=ArtifactType.RESPONSE,
            title="Lifecycle",
            content="Lifecycle test",
            producer=self.component_id,
        )

        return ComponentResult(
            artifact=artifact,
        )

    def after_execute(
        self,
        context: ComponentContext,
        result: ComponentResult,
    ) -> None:

        self.events.append(
            "after",
        )


def test_component_lifecycle():

    workflow = Workflow()

    node = WorkflowNode(
        id="step_1",
        component_id="lifecycle_test",
        objective="Test lifecycle",
        expected_output="Artifact",
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

    component = LifecycleComponent()

    result = component.invoke(
        context,
    )

    assert result.artifact.content == (
        "Lifecycle test"
    )

    assert component.events == [
        "before",
        "execute",
        "after",
    ]

    def test_component_lifecycle_stops_after_execute_failure():

        class FailingComponent(
            LifecycleComponent,
        ):

            component_id = "failing"

            def execute(
                self,
                context: ComponentContext,
            ) -> ComponentResult:

                self.events.append(
                    "execute",
                )

                raise RuntimeError(
                    "Component failed.",
                )

        workflow = Workflow()

        node = WorkflowNode(
            id="step_1",
            component_id="failing",
            objective="Test failure",
            expected_output="Artifact",
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

        component = FailingComponent()

        try:

            component.invoke(
                context,
            )

            assert False, (
                "Expected RuntimeError"
            )

        except RuntimeError as exc:

            assert str(exc) == (
                "Component failed."
            )

        assert component.events == [
            "before",
            "execute",
        ]