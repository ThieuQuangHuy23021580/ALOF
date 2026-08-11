from __future__ import annotations

from backend.application.orchestration.execution_request import (
    ExecutionRequest,
)
from backend.application.orchestration.learning_orchestrator import (
    LearningOrchestrator,
)
from backend.application.planning.sequential_planner import (
    SequentialPlanner,
)
from backend.application.planning.sequential_workflow_builder import (
    SequentialWorkflowBuilder,
)
from backend.application.routing.router import Router
from backend.application.routing.routing_result import (
    RoutingResult,
)
from backend.application.runtime.sequential_runtime import (
    SequentialRuntime,
)
from backend.core.component import Component
from backend.core.component_registry import (
    ComponentRegistry,
)
from backend.core.component_result import ComponentResult
from backend.domain.artifact.artifact import Artifact
from backend.domain.artifact.artifact_type import ArtifactType
from backend.domain.student.student import Student


class FakeRouter(Router):

    def route(
        self,
        student: Student,
        message: str,
    ) -> RoutingResult:

        return RoutingResult(
            intent="explain",
            candidate_components=[
                "metrics_fake",
            ],
            confidence=1.0,
        )


class MetricsFakeComponent(Component):

    component_id = "metrics_fake"

    name = "Metrics Fake"

    description = "Component for metrics testing."

    def execute(
        self,
        context,
    ) -> ComponentResult:

        artifact = Artifact(
            type=ArtifactType.RESPONSE,
            title="Metrics Test",
            content="Metrics OK",
            producer=self.component_id,
        )

        return ComponentResult(
            artifact=artifact,
        )


def test_learning_orchestrator_metrics():

    ComponentRegistry.clear()

    ComponentRegistry.register(
        MetricsFakeComponent,
    )

    orchestrator = LearningOrchestrator(
        router=FakeRouter(),
        planner=SequentialPlanner(),
        workflow_builder=SequentialWorkflowBuilder(),
        runtime=SequentialRuntime(),
    )

    request = ExecutionRequest(
        student=Student(
            display_name="Metrics Test Student",
        ),
        message="Explain Python",
    )

    result = orchestrator.execute(
        request,
    )

    assert result.status.value == "completed"

    assert result.execution_count == 1

    assert result.artifact_count == 1

    assert result.last_node_id == "step_1"

    assert result.final_artifact is not None

    assert result.final_artifact.content == (
        "Metrics OK"
    )

    assert result.duration is not None

    assert result.duration >= 0