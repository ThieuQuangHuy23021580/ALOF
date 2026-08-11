from __future__ import annotations

from backend.application.runtime.runtime_context import (
    RuntimeContext,
)
from backend.core.component import Component
from backend.core.component_context import ComponentContext
from backend.core.component_result import ComponentResult
from backend.core.default_component_executor import (
    DefaultComponentExecutor,
)
from backend.domain.artifact.artifact import Artifact
from backend.domain.artifact.artifact_type import ArtifactType
from backend.domain.workflow.workflow import Workflow
from backend.domain.workflow.workflow_node import WorkflowNode


class FakeComponent(Component):

    component_id = "executor_test"

    name = "Executor Test"

    description = "Test component executor."

    def execute(
        self,
        context: ComponentContext,
    ) -> ComponentResult:

        artifact = Artifact(
            type=ArtifactType.RESPONSE,
            title="Executor Test",
            content="Hello Executor",
            producer=self.component_id,
        )

        return ComponentResult(
            artifact=artifact,
        )


def test_default_component_executor_persists_artifact():

    workflow = Workflow()

    node = WorkflowNode(
        id="step_1",
        component_id="executor_test",
        objective="Test executor",
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

    component = FakeComponent()

    executor = DefaultComponentExecutor()

    result = executor.execute(
        component=component,
        context=context,
    )

    assert result.artifact.content == (
        "Hello Executor"
    )

    assert runtime.has_artifact(
        "step_1",
    )

    artifact = runtime.get_artifact(
        "step_1",
    )

    assert artifact is not None

    assert artifact.content == (
        "Hello Executor"
    )

    def test_default_component_executor_does_not_persist_failed_component():

        class FailingComponent(Component):

            component_id = "failing_executor_test"

            name = "Failing Executor Test"

            description = "Test failed execution."

            def execute(
                self,
                context: ComponentContext,
            ) -> ComponentResult:

                raise RuntimeError(
                    "Component execution failed.",
                )

        workflow = Workflow()

        node = WorkflowNode(
            id="step_1",
            component_id="failing_executor_test",
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

        executor = DefaultComponentExecutor()

        try:

            executor.execute(
                component=FailingComponent(),
                context=context,
            )

            assert False, (
                "Expected RuntimeError"
            )

        except RuntimeError as exc:

            assert str(exc) == (
                "Component execution failed."
            )

        assert not runtime.has_artifact(
            "step_1",
        )