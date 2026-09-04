from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from backend.domain.learning.learning_interaction import (
    LearningInteraction,
)


class HistoricalEvidence(BaseModel):
    """
    Represents historical learning evidence selected
    for the current tutoring task.

    HistoricalEvidence is an intermediate representation
    between raw learner interactions and knowledge
    state diagnosis.

    It preserves the semantic distinction between:

    - relevant interactions;
    - recent interactions;
    - related-concept interactions.

    It does not perform diagnosis itself.
    """

    learner_id: str

    current_question: str = ""

    relevant_interactions: list[LearningInteraction] = Field(
        default_factory=list,
    )

    recent_interactions: list[LearningInteraction] = Field(
        default_factory=list,
    )

    related_interactions: list[LearningInteraction] = Field(
        default_factory=list,
    )

    related_concept_ids: list[str] = Field(
        default_factory=list,
    )

    metadata: dict[str, object] = Field(
        default_factory=dict,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(
            UTC,
        ),
    )

    # ======================================================
    # Interaction management
    # ======================================================

    def add_relevant_interaction(
        self,
        interaction: LearningInteraction,
    ) -> None:
        """
        Add an interaction as directly relevant
        historical evidence.
        """

        self.relevant_interactions.append(
            interaction,
        )

    def add_recent_interaction(
        self,
        interaction: LearningInteraction,
    ) -> None:
        """
        Add an interaction to recent-history evidence.
        """

        self.recent_interactions.append(
            interaction,
        )

    def add_related_interaction(
        self,
        interaction: LearningInteraction,
    ) -> None:
        """
        Add an interaction as related-concept evidence.

        Related evidence is intentionally kept separate
        from directly relevant evidence so downstream
        selectors can preserve source semantics.
        """

        self.related_interactions.append(
            interaction,
        )

    # ======================================================
    # Concept management
    # ======================================================

    def add_related_concept(
        self,
        concept_id: str,
    ) -> None:
        """
        Register a concept related to the current task.
        """

        if concept_id not in self.related_concept_ids:
            self.related_concept_ids.append(
                concept_id,
            )

    # ======================================================
    # Metadata
    # ======================================================

    def set_metadata(
        self,
        key: str,
        value: object,
    ) -> None:
        """
        Store evidence metadata.
        """

        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default: object = None,
    ) -> object:
        """
        Retrieve evidence metadata.
        """

        return self.metadata.get(
            key,
            default,
        )

    # ======================================================
    # Inspection
    # ======================================================

    @property
    def interaction_count(self) -> int:
        """
        Return the total number of selected historical
        interactions across all evidence categories.
        """

        return (
            len(self.relevant_interactions)
            + len(self.recent_interactions)
            + len(self.related_interactions)
        )

    @property
    def has_evidence(self) -> bool:
        """
        Return whether historical evidence is available.
        """

        return self.interaction_count > 0