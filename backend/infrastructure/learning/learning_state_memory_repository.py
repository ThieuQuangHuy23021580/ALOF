from __future__ import annotations

from datetime import UTC

from backend.domain.learning.learning_interaction import (
    LearningInteraction,
)
from backend.domain.learning.learning_state import LearningState
from backend.domain.learning.memory_repository import MemoryRepository


def _concept_set(values: list[str]) -> set[str]:
    return {
        str(value).strip().lower()
        for value in values
        if value is not None and str(value).strip()
    }


class LearningStateMemoryRepository(MemoryRepository):
    """In-memory learner history used by the benchmark runtime."""

    def __init__(self, learning_state: LearningState) -> None:
        self._state = learning_state

    def get_recent_interactions(
        self,
        learner_id: str,
        limit: int,
    ) -> list[LearningInteraction]:
        interactions = [
            interaction
            for interaction in self._state.interactions
            if interaction.learner_id == learner_id
        ]
        interactions.sort(
            key=lambda item: item.timestamp.astimezone(UTC)
            if item.timestamp.tzinfo
            else item.timestamp.replace(tzinfo=UTC),
            reverse=True,
        )
        if limit <= 0:
            return interactions
        return interactions[:limit]

    def get_interactions_by_concepts(
        self,
        learner_id: str,
        concept_ids: list[str],
        limit: int,
    ) -> list[LearningInteraction]:
        targets = _concept_set(concept_ids)
        if not targets:
            return self.get_recent_interactions(learner_id, limit)

        matches = [
            interaction
            for interaction in self.get_recent_interactions(
                learner_id,
                limit=0,
            )
            if targets & _concept_set(interaction.concept_ids)
        ]
        if limit <= 0:
            return matches
        return matches[:limit]
