from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from backend.application.orchestration.adaptive_learning_result import (
    AdaptiveLearningResult,
)
from backend.application.routing.routing_result import (
    RoutingResult,
)
from backend.domain.learning.learning_state import (
    LearningState,
)
from backend.domain.student.student import (
    Student,
)


class PlanningRequest(BaseModel):
    """
    Input for the planning stage.

    Encapsulates all information required by a Planner
    to generate an execution plan.

    Adaptive learning results are passed as one cohesive
    object so that HistoricalEvidence, KnowledgeDiagnosis,
    and AdaptiveTeachingAction remain consistent.
    """

    student: Student

    message: str

    routing: RoutingResult

    learning_state: LearningState = Field(
        default_factory=lambda: LearningState(
            learner_id="default",
        ),
    )

    adaptive_learning: AdaptiveLearningResult

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    # ======================================================
    # Metadata
    # ======================================================

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.metadata.get(
            key,
            default,
        )