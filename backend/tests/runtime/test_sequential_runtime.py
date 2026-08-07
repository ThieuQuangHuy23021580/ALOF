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

from backend.core.component_result import (
    ComponentResult,
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

from backend.domain.workflow.workflow_edge import (
    WorkflowEdge,
)

class FakeComponent(Component):

    component_id = "fake"

    name = "Fake Component"

    description = "Testing component"

    def execute(
        self,
        context,
    ) -> ComponentResult:

        artifact = Artifact(
            type=ArtifactType.RESPONSE,
            title="Test",
            content="Hello Runtime",
            producer=self.component_id,
        )

        return ComponentResult(
            artifact=artifact,
        )


def test_sequential_runtime_execution():

    ComponentRegistry.clear()

    ComponentRegistry.register(
        FakeComponent,
    )


    workflow = Workflow()


    workflow.add_node(
        WorkflowNode(
            id="step_1",
            component_id="fake",
            objective="Generate response",
        )
    )


    context = RuntimeContext(
        workflow=workflow,
    )


    runtime = SequentialRuntime()


    result = runtime.run(
        context,
    )


    assert (
        result.status.value
        == "completed"
    )


    assert result.execution_order == [
        "step_1"
    ]


    assert (
        result.final_artifact is not None
    )


    assert (
        result.final_artifact.content
        == "Hello Runtime"
    )


    assert (
        result.duration is not None
    )

def test_sequential_runtime_dependency_execution():

    ComponentRegistry.clear()


    class FirstComponent(Component):

        component_id = "first"

        name = "First"

        description = "First step"


        def execute(
            self,
            context,
        ) -> ComponentResult:

            artifact = Artifact(
                type=ArtifactType.RESPONSE,
                title="First",
                content="First Result",
                producer=self.component_id,
            )

            return ComponentResult(
                artifact=artifact,
            )


    class SecondComponent(Component):

        component_id = "second"

        name = "Second"

        description = "Second step"


        def execute(
            self,
            context,
        ) -> ComponentResult:

            previous = (
                context.runtime.get_artifact(
                    "step_1",
                )
            )

            assert previous is not None

            artifact = Artifact(
                type=ArtifactType.RESPONSE,
                title="Second",
                content=(
                    "Second uses: "
                    + previous.content
                ),
                producer=self.component_id,
            )

            return ComponentResult(
                artifact=artifact,
            )


    ComponentRegistry.register(
        FirstComponent,
    )

    ComponentRegistry.register(
        SecondComponent,
    )


    workflow = Workflow()


    workflow.add_node(
        WorkflowNode(
            id="step_1",
            component_id="first",
            objective="First task",
        )
    )


    workflow.add_node(
        WorkflowNode(
            id="step_2",
            component_id="second",
            objective="Second task",
        )
    )


    workflow.add_edge(
        WorkflowEdge(
            from_node="step_1",
            to_node="step_2",
        )
    )


    context = RuntimeContext(
        workflow=workflow,
    )


    runtime = SequentialRuntime()


    result = runtime.run(
        context,
    )


    assert (
        result.status.value
        == "completed"
    )


    assert result.execution_order == [
        "step_1",
        "step_2",
    ]


    assert (
        result.final_artifact is not None
    )


    assert (
        result.final_artifact.content
        == "Second uses: First Result"
    )