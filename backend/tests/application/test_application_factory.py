from __future__ import annotations

from backend.application.application_factory import (
    ApplicationFactory,
)
from backend.application.services.learning_service import (
    LearningService,
)


def test_create_learning_service():

    service = (
        ApplicationFactory
        .create_learning_service()
    )

    assert isinstance(
        service,
        LearningService,
    )