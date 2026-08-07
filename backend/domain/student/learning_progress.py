from __future__ import annotations

from pydantic import BaseModel


class LearningProgress(BaseModel):
    """
    Represents the learner's current learning state.

    This object stores only the latest progress snapshot,
    not the complete learning history.
    """

    completed_topics: int = 0

    completed_sessions: int = 0

    mastered_topics: int = 0

    current_streak: int = 0

    total_learning_minutes: int = 0

    overall_mastery: float = 0.0

    def complete_topic(self) -> None:
        self.completed_topics += 1

    def complete_session(
        self,
        minutes: int,
    ) -> None:
        self.completed_sessions += 1
        self.total_learning_minutes += minutes

    def increase_mastery(
        self,
        delta: float,
    ) -> None:
        self.overall_mastery = min(
            1.0,
            self.overall_mastery + delta,
        )

    def reset_streak(self) -> None:
        self.current_streak = 0

    def increase_streak(self) -> None:
        self.current_streak += 1