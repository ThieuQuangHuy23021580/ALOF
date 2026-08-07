from __future__ import annotations

from abc import ABC, abstractmethod

from backend.domain.goal.learning_goal import LearningGoal


class GoalRepository(ABC):
    """
    Domain repository for LearningGoal Aggregate.
    """

    @abstractmethod
    def add(
        self,
        goal: LearningGoal,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        goal_id: str,
    ) -> LearningGoal | None:
        raise NotImplementedError

    @abstractmethod
    def list(
        self,
    ) -> list[LearningGoal]:
        raise NotImplementedError

    @abstractmethod
    def remove(
        self,
        goal_id: str,
    ) -> None:
        raise NotImplementedError