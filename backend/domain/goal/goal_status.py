from __future__ import annotations

from enum import StrEnum


class GoalStatus(StrEnum):
    """
    Current lifecycle state of a learning goal.
    """

    NOT_STARTED = "not_started"

    IN_PROGRESS = "in_progress"

    COMPLETED = "completed"

    PAUSED = "paused"

    CANCELLED = "cancelled"