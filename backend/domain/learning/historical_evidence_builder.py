from __future__ import annotations

from backend.domain.learning.historical_evidence import (
    HistoricalEvidence,
)
from backend.domain.learning.learning_interaction import (
    LearningInteraction,
)
from backend.domain.learning.learning_state import (
    LearningState,
)


class HistoricalEvidenceBuilder:
    """
    Builds historical evidence from the learner's
    existing learning history.

    Responsibilities
    ----------------
    - Select recent interactions.
    - Select interactions relevant to the current concepts.
    - Collect related concepts.
    - Keep evidence deterministic.
    - Never perform diagnosis.
    - Never call an LLM.
    """

    def __init__(
        self,
        recent_limit: int = 5,
    ) -> None:

        if recent_limit <= 0:
            raise ValueError(
                "recent_limit must be greater than 0."
            )

        self._recent_limit = recent_limit

    def build(
        self,
        learning_state: LearningState,
        current_question: str = "",
        related_concept_ids: list[str] | None = None,
    ) -> HistoricalEvidence:
        """
        Build historical evidence for the current task.
        """

        interactions = list(
            learning_state.interactions
        )

        relevant_concepts = set(
            related_concept_ids or []
        )

        evidence = HistoricalEvidence(
            learner_id=learning_state.learner_id,
            current_question=current_question,
        )

        # ------------------------------------------------------
        # Recent evidence
        # ------------------------------------------------------

        recent_interactions = sorted(
            interactions,
            key=lambda interaction: interaction.timestamp,
        )[-self._recent_limit:]

        for interaction in recent_interactions:

            evidence.add_recent_interaction(
                interaction,
            )

            for concept_id in interaction.concept_ids:
                evidence.add_related_concept(
                    concept_id,
                )

        # ------------------------------------------------------
        # Relevant evidence
        # ------------------------------------------------------

        if relevant_concepts:

            for interaction in interactions:

                if relevant_concepts.intersection(
                    interaction.concept_ids
                ):
                    evidence.add_relevant_interaction(
                        interaction,
                    )

                    for concept_id in interaction.concept_ids:
                        evidence.add_related_concept(
                            concept_id,
                        )

        # ------------------------------------------------------
        # Metadata
        # ------------------------------------------------------

        evidence.set_metadata(
            "selection_strategy",
            "recent_and_related_concepts",
        )

        evidence.set_metadata(
            "recent_limit",
            self._recent_limit,
        )

        evidence.set_metadata(
            "source_interaction_count",
            len(interactions),
        )

        evidence.set_metadata(
            "recent_interaction_count",
            len(
                evidence.recent_interactions
            ),
        )

        evidence.set_metadata(
            "relevant_interaction_count",
            len(
                evidence.relevant_interactions
            ),
        )

        return evidence