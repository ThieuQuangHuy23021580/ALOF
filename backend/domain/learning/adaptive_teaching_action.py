from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from backend.domain.learning.knowledge_diagnosis import (
    KnowledgeDiagnosis,
)
from backend.domain.learning.knowledge_diagnosis import (
    ConceptDiagnosis,
)


class TeachingActionType(StrEnum):
    """
    Represents the adaptive teaching action selected
    for the current learner state.
    """

    INTRODUCE = "introduce"

    EXPLAIN = "explain"

    SCAFFOLD = "scaffold"

    PRACTICE = "practice"

    REVIEW = "review"

    CHALLENGE = "challenge"


class TeachingStrategy(StrEnum):
    """
    Represents the teaching strategy selected for
    the current adaptive action.
    """

    DIRECT_EXPLANATION = "direct_explanation"

    GUIDED_EXPLANATION = "guided_explanation"

    STEP_BY_STEP = "step_by_step"

    TARGETED_PRACTICE = "targeted_practice"

    SPACED_REVIEW = "spaced_review"

    DEEPENING = "deepening"


class AdaptiveTeachingAction(BaseModel):
    """
    Represents the adaptive teaching decision for
    the current tutoring task.

    This is a domain-level decision.

    It does not execute teaching and does not call
    an LLM.
    """

    action: TeachingActionType

    strategy: TeachingStrategy

    difficulty: str = "medium"

    focus_concepts: list[str] = Field(
        default_factory=list,
    )

    reason: str = ""

    metadata: dict[str, object] = Field(
        default_factory=dict,
    )

    @property
    def has_focus(self) -> bool:
        return bool(
            self.focus_concepts
        )

    def add_focus_concept(
        self,
        concept_id: str,
    ) -> None:

        if concept_id not in self.focus_concepts:
            self.focus_concepts.append(
                concept_id,
            )

    def set_metadata(
        self,
        key: str,
        value: object,
    ) -> None:

        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default: object = None,
    ) -> object:

        return self.metadata.get(
            key,
            default,
        )


class AdaptiveTeachingActionSelector:
    """
    Deterministically selects an adaptive teaching action
    from KnowledgeDiagnosis.

    Responsibilities
    ----------------
    - Identify the learner's current instructional need.
    - Select an appropriate teaching action.
    - Select an appropriate teaching strategy.
    - Select an appropriate difficulty.
    - Select concepts requiring attention.
    - Never modify LearningState.
    - Never call an LLM.
    """

    def __init__(
        self,
        weak_mastery_threshold: float = 0.4,
        strong_mastery_threshold: float = 0.7,
    ) -> None:

        if not 0.0 <= weak_mastery_threshold <= 1.0:
            raise ValueError(
                "weak_mastery_threshold must be between 0 and 1."
            )

        if not 0.0 <= strong_mastery_threshold <= 1.0:
            raise ValueError(
                "strong_mastery_threshold must be between 0 and 1."
            )

        if (
            weak_mastery_threshold
            >= strong_mastery_threshold
        ):
            raise ValueError(
                "weak_mastery_threshold must be lower "
                "than strong_mastery_threshold."
            )

        self._weak_mastery_threshold = (
            weak_mastery_threshold
        )

        self._strong_mastery_threshold = (
            strong_mastery_threshold
        )

    def select(
        self,
        diagnosis: KnowledgeDiagnosis,
    ) -> AdaptiveTeachingAction:
        """
        Select an adaptive teaching action from
        the learner diagnosis.
        """

        if not diagnosis.concepts:
            return AdaptiveTeachingAction(
                action=TeachingActionType.INTRODUCE,
                strategy=TeachingStrategy.DIRECT_EXPLANATION,
                difficulty="beginner",
                reason=(
                    "No diagnosed knowledge state is available "
                    "for the current task."
                ),
            )

        # ------------------------------------------------------
        # Transfer deficit has highest priority.
        # ------------------------------------------------------

        if diagnosis.transfer_deficit_concepts:

            action = AdaptiveTeachingAction(
                action=TeachingActionType.SCAFFOLD,
                strategy=TeachingStrategy.STEP_BY_STEP,
                difficulty="medium",
                reason=(
                    "The learner has difficulty applying "
                    "related knowledge to the current task."
                ),
            )

            for concept_id in (
                diagnosis.transfer_deficit_concepts
            ):
                action.add_focus_concept(
                    concept_id,
                )

            action.set_metadata(
                "decision_signal",
                "transfer_deficit",
            )

            return action

        # ------------------------------------------------------
        # Weak concepts require guided teaching.
        # ------------------------------------------------------

        if diagnosis.weak_concepts:

            action = AdaptiveTeachingAction(
                action=TeachingActionType.EXPLAIN,
                strategy=TeachingStrategy.GUIDED_EXPLANATION,
                difficulty="beginner",
                reason=(
                    "The learner has insufficient mastery "
                    "of one or more required concepts."
                ),
            )

            for concept_id in (
                diagnosis.weak_concepts
            ):
                action.add_focus_concept(
                    concept_id,
                )

            action.set_metadata(
                "decision_signal",
                "weak_knowledge",
            )

            return action

        # ------------------------------------------------------
        # Strong knowledge can be challenged.
        # ------------------------------------------------------

        strong_concepts = [
            concept_id
            for concept_id, concept in (
                diagnosis.concepts.items()
            )
            if (
                concept.mastery
                >= self._strong_mastery_threshold
            )
        ]

        if strong_concepts:

            action = AdaptiveTeachingAction(
                action=TeachingActionType.CHALLENGE,
                strategy=TeachingStrategy.DEEPENING,
                difficulty="advanced",
                reason=(
                    "The learner demonstrates strong mastery "
                    "of the relevant concepts."
                ),
            )

            for concept_id in strong_concepts:
                action.add_focus_concept(
                    concept_id,
                )

            action.set_metadata(
                "decision_signal",
                "strong_mastery",
            )

            return action

        # ------------------------------------------------------
        # Existing but incomplete knowledge.
        # ------------------------------------------------------

        intermediate_concepts = [
            concept_id
            for concept_id, concept in (
                diagnosis.concepts.items()
            )
            if (
                self._weak_mastery_threshold
                <= concept.mastery
                < self._strong_mastery_threshold
            )
        ]

        if intermediate_concepts:

            action = AdaptiveTeachingAction(
                action=TeachingActionType.PRACTICE,
                strategy=TeachingStrategy.TARGETED_PRACTICE,
                difficulty="medium",
                reason=(
                    "The learner has partial mastery and "
                    "should consolidate the knowledge through practice."
                ),
            )

            for concept_id in intermediate_concepts:
                action.add_focus_concept(
                    concept_id,
                )

            action.set_metadata(
                "decision_signal",
                "partial_mastery",
            )

            return action

        # ------------------------------------------------------
        # Fallback.
        # ------------------------------------------------------

        return AdaptiveTeachingAction(
            action=TeachingActionType.REVIEW,
            strategy=TeachingStrategy.SPACED_REVIEW,
            difficulty="medium",
            reason=(
                "Review the relevant knowledge before "
                "continuing with the current task."
            ),
        )