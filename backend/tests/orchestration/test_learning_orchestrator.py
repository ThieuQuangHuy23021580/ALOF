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

from backend.core.component_result import (
    ComponentResult,
)

from backend.domain.artifact.artifact import (
    Artifact,
)

from backend.domain.artifact.artifact_type import (
    ArtifactType,
)

from backend.domain.student.student import (
    Student,
)


# ==========================================================
# Fake Router
# ==========================================================

class FakeRouter(Router):

    def route(
        self,
        student: Student,
        message: str,
    ) -> RoutingResult:

        return RoutingResult(
            intent="explain",
            candidate_components=[
                "fake",
            ],
            confidence=1.0,
        )


# ==========================================================
# Fake Component
# ==========================================================

class FakeComponent(Component):

    component_id = "fake"

    name = "Fake"

    description = "Fake component"


    def execute(
        self,
        context,
    ) -> ComponentResult:

        artifact = Artifact(
            type=ArtifactType.RESPONSE,
            title="Fake Result",
            content="Hello Orchestrator",
            producer=self.component_id,
        )

        return ComponentResult(
            artifact=artifact,
        )


# ==========================================================
# Test
# ==========================================================

def test_learning_orchestrator_execution():

    ComponentRegistry.clear()

    ComponentRegistry.register(
        FakeComponent,
    )


    orchestrator = LearningOrchestrator(
        router=FakeRouter(),
        planner=SequentialPlanner(),
        workflow_builder=SequentialWorkflowBuilder(),
        runtime=SequentialRuntime(),
    )


    request = ExecutionRequest(
        student=Student(
            display_name="Test Student",
        ),
        message="Explain Python",
    )


    result = orchestrator.execute(
        request,
    )


    assert (
        result.status.value
        == "completed"
    )


    assert result.execution_order == [
        "step_1",
    ]


    assert (
        result.final_artifact is not None
    )


    assert (
        result.final_artifact.content
        == "Hello Orchestrator"
    )