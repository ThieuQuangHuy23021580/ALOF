from __future__ import annotations

from backend.application.orchestration.execution_request import (
    ExecutionRequest,
)
from backend.application.runtime.runtime_result import (
    RuntimeResult,
)
from backend.application.services.learning_service import (
    LearningService,
)
from backend.core.execution_status import ExecutionStatus
from backend.domain.artifact.artifact import Artifact
from backend.domain.artifact.artifact_type import ArtifactType
from backend.domain.student.student import Student


class FakeLearningOrchestrator:
    """
    Fake orchestrator for testing LearningService.
    """

    def execute(
        self,
        request: ExecutionRequest,
    ) -> RuntimeResult:

        artifact = Artifact(
            type=ArtifactType.RESPONSE,
            title="Test Result",
            content="Hello Learning Service",
            producer="fake",
        )

        return RuntimeResult(
            status=ExecutionStatus.COMPLETED,
            artifacts={
                "step_1": artifact,
            },
            final_artifact=artifact,
            execution_order=[
                "step_1",
            ],
            duration=0.1,
        )


def test_learning_service_execution():

    service = LearningService(
        orchestrator=FakeLearningOrchestrator(),
    )

    request = ExecutionRequest(
        student=Student(
            display_name="Test Student",
        ),
        message="Explain Python",
    )

    result = service.execute(
        request,
    )

    assert (
        result.status
        == ExecutionStatus.COMPLETED
    )

    assert result.execution_order == [
        "step_1",
    ]

    assert (
        result.final_artifact is not None
    )

    assert (
        result.final_artifact.content
        == "Hello Learning Service"
    )