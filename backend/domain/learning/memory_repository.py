from __future__ import annotations

from abc import ABC, abstractmethod

from backend.domain.learning.learning_interaction import (
    LearningInteraction,
)


class MemoryRepository(ABC):
    """
    Learner-scoped historical interaction retrieval.

    Ranking stays in the application layer.
    """

    @abstractmethod
    def get_recent_interactions(
        self,
        learner_id: str,
        limit: int,
    ) -> list[LearningInteraction]:
        raise NotImplementedError

    @abstractmethod
    def get_interactions_by_concepts(
        self,
        learner_id: str,
        concept_ids: list[str],
        limit: int,
    ) -> list[LearningInteraction]:
        raise NotImplementedError
