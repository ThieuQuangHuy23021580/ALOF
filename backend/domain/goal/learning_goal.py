from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from pydantic import BaseModel, Field

from backend.domain.goal.goal_status import GoalStatus


class LearningGoal(BaseModel):
    """
    Aggregate Root representing a learner's goal.

    A goal drives workflow planning and progress tracking.
    """

    id: str = Field(
        default_factory=lambda: str(uuid4()),
    )

    student_id: str

    knowledge_node_id: str

    target_level: str

    status: GoalStatus = GoalStatus.NOT_STARTED

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(
            UTC,
        ),
    )

    completed_at: datetime | None = None

    def start(
        self,
    ) -> None:

        self.status = GoalStatus.IN_PROGRESS

    def complete(
        self,
    ) -> None:

        self.status = GoalStatus.COMPLETED
        self.completed_at = datetime.now(
            UTC,
        )

    def pause(
        self,
    ) -> None:

        self.status = GoalStatus.PAUSED

    def cancel(
        self,
    ) -> None:

        self.status = GoalStatus.CANCELLED