
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
from backend.core.component_context import ComponentContext
from backend.core.component_registry import (
    ComponentRegistry,
)
from backend.core.component_result import (
    ComponentResult,
)
from backend.domain.artifact.artifact import Artifact
from backend.domain.artifact.artifact_type import (
    ArtifactType,
)
from backend.domain.student.student import Student


class FakeRouter(Router):
    """
    Fake router for end-to-end testing.

    It avoids calling the real LLM.
    """

    def route(
        self,
        student: Student,
        message: str,
    ) -> RoutingResult:

        return RoutingResult(
            intent="explain",
            confidence=1.0,
            candidate_components=[
                "fake_mentor",
            ],
        )


class FakeMentorComponent(Component):
    """
    Fake Mentor component for end-to-end testing.
    """

    component_id = "fake_mentor"

    name = "Fake Mentor"

    description = (
        "Fake mentor component for testing."
    )

    def execute(
        self,
        context: ComponentContext,
    ) -> ComponentResult:

        artifact = Artifact(
            type=ArtifactType.LESSON,
            title="Test Lesson",
            content="Hello from E2E pipeline",
            producer=self.component_id,
        )

        return ComponentResult(
            artifact=artifact,
        )


def test_learning_orchestrator_end_to_end():

    ComponentRegistry.clear()

    ComponentRegistry.register(
        FakeMentorComponent,
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
        == "Hello from E2E pipeline"
    )

    assert (
        result.final_artifact.producer
        == "fake_mentor"
    )

