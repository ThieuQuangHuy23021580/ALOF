from __future__ import annotations

from backend.application.runtime.runtime_result import (
    RuntimeResult,
)
from backend.core.execution_status import ExecutionStatus
from backend.domain.artifact.artifact import Artifact
from backend.domain.artifact.artifact_type import ArtifactType


def test_runtime_result_defaults():

    result = RuntimeResult(
        status=ExecutionStatus.CREATED,
    )

    assert result.status == ExecutionStatus.CREATED

    assert result.artifacts == {}

    assert result.final_artifact is None

    assert result.execution_order == []

    assert result.duration is None

    assert result.metadata == {}


def test_runtime_result_contains_execution_data():

    artifact = Artifact(
        type=ArtifactType.RESPONSE,
        title="Test",
        content="Hello",
        producer="test",
    )

    result = RuntimeResult(
        status=ExecutionStatus.COMPLETED,
        artifacts={
            "step_1": artifact,
        },
        final_artifact=artifact,
        execution_order=[
            "step_1",
        ],
        duration=1.25,
        metadata={
            "test": "value",
        },
    )

    assert result.status == (
        ExecutionStatus.COMPLETED
    )

    assert result.artifacts["step_1"] is artifact

    assert result.final_artifact is artifact

    assert result.execution_order == [
        "step_1",
    ]

    assert result.duration == 1.25

    assert result.metadata["test"] == "value"


def test_runtime_result_metadata():

    result = RuntimeResult(
        status=ExecutionStatus.COMPLETED,
    )

    result.add_metadata(
        "execution_id",
        "test-001",
    )

    result.add_metadata(
        "component_count",
        3,
    )

    assert result.metadata["execution_id"] == (
        "test-001"
    )

    assert result.metadata["component_count"] == 3


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


class ResultComponent(Component):

    component_id = "result_test"

    name = "Result Test"

    description = "Test runtime result."

    def execute(
        self,
        context,
    ) -> ComponentResult:

        artifact = Artifact(
            type=ArtifactType.RESPONSE,
            title="Result",
            content="Runtime Result",
            producer=self.component_id,
        )

        return ComponentResult(
            artifact=artifact,
        )


def test_sequential_runtime_builds_runtime_result():

    ComponentRegistry.clear()

    ComponentRegistry.register(
        ResultComponent,
    )

    workflow = Workflow()

    workflow.add_node(
        WorkflowNode(
            id="step_1",
            component_id="result_test",
            objective="Test result",
            expected_output="Artifact",
        )
    )

    context = RuntimeContext(
        workflow=workflow,
    )

    runtime = SequentialRuntime()

    result = runtime.run(
        context,
    )

    assert result.status == (
        ExecutionStatus.COMPLETED
    )

    assert result.execution_order == [
        "step_1",
    ]

    assert "step_1" in result.artifacts

    assert result.final_artifact is not None

    assert result.final_artifact.content == (
        "Runtime Result"
    )

    assert result.duration is not None

def test_runtime_result_execution_metrics():

    result = RuntimeResult(
        status=ExecutionStatus.COMPLETED,
        execution_order=[
            "step_1",
            "step_2",
            "step_3",
        ],
        artifacts={
            "step_1": Artifact(
                type=ArtifactType.RESPONSE,
                title="One",
                content="One",
                producer="test",
            ),
            "step_2": Artifact(
                type=ArtifactType.RESPONSE,
                title="Two",
                content="Two",
                producer="test",
            ),
        },
    )

    assert result.execution_count == 3

    assert result.artifact_count == 2

    assert result.last_node_id == "step_3"

def test_runtime_result_empty_metrics():

    result = RuntimeResult(
        status=ExecutionStatus.CREATED,
    )

    assert result.execution_count == 0

    assert result.artifact_count == 0

    assert result.last_node_id is None