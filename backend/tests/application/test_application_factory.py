
from __future__ import annotations

from backend.application.application_factory import (
    ApplicationFactory,
)
from backend.application.orchestration.learning_orchestrator import (
    LearningOrchestrator,
)


def test_create_orchestrator():

    orchestrator = (
        ApplicationFactory
        .create_orchestrator()
    )

    assert isinstance(
        orchestrator,
        LearningOrchestrator,
    )
