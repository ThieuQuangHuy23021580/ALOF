from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from backend.domain.knowledge.knowledge_level import (
    KnowledgeLevel,
)


class KnowledgeState(BaseModel):
    """
    Represents the learner's current state for a
    specific knowledge concept.

    This is learner-specific state and must not be
    confused with KnowledgeNode, which belongs to
    the domain knowledge model.
    """

    concept_id: str

    mastery: float = 0.0

    level: KnowledgeLevel = KnowledgeLevel.UNKNOWN

    attempts: int = 0

    correct_attempts: int = 0

    error_rate: float = 0.0

    recent_accuracy: float = 0.0

    last_interaction_at: datetime | None = None

    metadata: dict[str, object] = Field(
        default_factory=dict,
    )

    def record_attempt(
        self,
        correct: bool,
    ) -> None:
        """
        Record one learner interaction with this concept.
        """

        self.attempts += 1

        if correct:
            self.correct_attempts += 1

        self.error_rate = (
            1.0
            - (
                self.correct_attempts
                / self.attempts
            )
        )

        self.recent_accuracy = (
            self.correct_attempts
            / self.attempts
        )

        self.last_interaction_at = (
            datetime.now(UTC)
        )

    def update_mastery(
        self,
        value: float,
    ) -> None:
        """
        Update estimated mastery.

        Mastery is normalized to [0, 1].
        """

        self.mastery = max(
            0.0,
            min(1.0, value),
        )

        self.level = self._infer_level()

    def _infer_level(
        self,
    ) -> KnowledgeLevel:
        """
        Infer knowledge level from mastery.

        Level is derived from mastery and does not
        require previous learner interactions.

        This is important because an initial learner
        state may already contain an estimated mastery
        value before any interaction is recorded.
        """

        if self.mastery <= 0.0:
            return KnowledgeLevel.UNKNOWN

        if self.mastery < 0.4:
            return KnowledgeLevel.BEGINNER

        if self.mastery < 0.7:
            return KnowledgeLevel.INTERMEDIATE

        if self.mastery < 0.9:
            return KnowledgeLevel.ADVANCED

        return KnowledgeLevel.MASTERED