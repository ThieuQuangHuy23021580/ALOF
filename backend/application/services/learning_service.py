from __future__ import annotations

from backend.application.orchestration.execution_request import (
    ExecutionRequest,
)
from backend.application.orchestration.learning_orchestrator import (
    LearningOrchestrator,
)
from backend.application.runtime.runtime_result import (
    RuntimeResult,
)


class LearningService:
    """
    Application service for executing a learner request.

    LearningService is the entry point for the application
    layer.

    Responsibilities
    ----------------
    - Receive an ExecutionRequest.
    - Delegate execution to LearningOrchestrator.
    - Return the final RuntimeResult.

    It does not perform:
    - intent recognition
    - component selection
    - planning
    - workflow construction
    - runtime execution
    """

    def __init__(
        self,
        orchestrator: LearningOrchestrator,
    ) -> None:

        self._orchestrator = orchestrator

    def execute(
        self,
        request: ExecutionRequest,
    ) -> RuntimeResult:

        return self._orchestrator.execute(
            request,
        )