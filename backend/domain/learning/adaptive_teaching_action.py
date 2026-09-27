from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from backend.domain.learning.knowledge_diagnosis import (
    KnowledgeDiagnosis,
)


class TeachingActionType(StrEnum):
    INTRODUCE = "introduce"
    EXPLAIN = "explain"
    SCAFFOLD = "scaffold"
    PRACTICE = "practice"
    REVIEW = "review"
    CHALLENGE = "challenge"


class TeachingStrategy(StrEnum):
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
        return bool(self.focus_concepts)

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
    - Use adaptive quiz target ranking when available.
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

        adaptive_targets = self._get_adaptive_targets(
            diagnosis,
        )

        introduce_concepts = [
            concept_id
            for concept_id in diagnosis.primary_concepts
            if (
                concept_id in diagnosis.concepts
                and diagnosis.concepts[concept_id].attempts == 0
                and not diagnosis.concepts[
                    concept_id
                ].has_relevant_evidence
                and not diagnosis.concepts[
                    concept_id
                ].has_recent_evidence
            )
        ]

        if introduce_concepts:

            focus_concepts = self._prioritize_concepts(
                introduce_concepts,
                adaptive_targets,
            )

            return AdaptiveTeachingAction(
                action=TeachingActionType.INTRODUCE,
                strategy=TeachingStrategy.DIRECT_EXPLANATION,
                difficulty="beginner",
                focus_concepts=focus_concepts,
                reason=(
                    "The learner has no prior knowledge "
                    "or historical evidence for the required concept."
                ),
            )

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

        if diagnosis.transfer_deficit_concepts:

            focus_concepts = self._prioritize_concepts(
                diagnosis.transfer_deficit_concepts,
                adaptive_targets,
            )

            action = AdaptiveTeachingAction(
                action=TeachingActionType.SCAFFOLD,
                strategy=TeachingStrategy.STEP_BY_STEP,
                difficulty="medium",
                focus_concepts=focus_concepts,
                reason=(
                    "The learner has difficulty applying "
                    "related knowledge to the current task."
                ),
            )

            action.set_metadata(
                "decision_signal",
                "transfer_deficit",
            )

            self._attach_target_metadata(
                action,
                adaptive_targets,
            )

            return action

        if diagnosis.weak_concepts:

            focus_concepts = self._prioritize_concepts(
                diagnosis.weak_concepts,
                adaptive_targets,
            )

            action = AdaptiveTeachingAction(
                action=TeachingActionType.EXPLAIN,
                strategy=TeachingStrategy.GUIDED_EXPLANATION,
                difficulty="beginner",
                focus_concepts=focus_concepts,
                reason=(
                    "The learner has insufficient mastery "
                    "of one or more required concepts."
                ),
            )

            action.set_metadata(
                "decision_signal",
                "weak_knowledge",
            )

            self._attach_target_metadata(
                action,
                adaptive_targets,
            )

            return action

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

            focus_concepts = self._prioritize_concepts(
                strong_concepts,
                adaptive_targets,
            )

            action = AdaptiveTeachingAction(
                action=TeachingActionType.CHALLENGE,
                strategy=TeachingStrategy.DEEPENING,
                difficulty="advanced",
                focus_concepts=focus_concepts,
                reason=(
                    "The learner demonstrates strong mastery "
                    "of the relevant concepts."
                ),
            )

            action.set_metadata(
                "decision_signal",
                "strong_mastery",
            )

            self._attach_target_metadata(
                action,
                adaptive_targets,
            )

            return action

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

            focus_concepts = self._prioritize_concepts(
                intermediate_concepts,
                adaptive_targets,
            )

            action = AdaptiveTeachingAction(
                action=TeachingActionType.PRACTICE,
                strategy=TeachingStrategy.TARGETED_PRACTICE,
                difficulty="medium",
                focus_concepts=focus_concepts,
                reason=(
                    "The learner has partial mastery and "
                    "should consolidate the knowledge through practice."
                ),
            )

            action.set_metadata(
                "decision_signal",
                "partial_mastery",
            )

            self._attach_target_metadata(
                action,
                adaptive_targets,
            )

            return action

        return AdaptiveTeachingAction(
            action=TeachingActionType.REVIEW,
            strategy=TeachingStrategy.SPACED_REVIEW,
            difficulty="medium",
            reason=(
                "Review the relevant knowledge before "
                "continuing with the current task."
            ),
        )

    @staticmethod
    def _get_adaptive_targets(
        diagnosis: KnowledgeDiagnosis,
    ) -> list[tuple[str, float]]:

        metadata = diagnosis.metadata

        if not isinstance(
            metadata,
            dict,
        ):
            return []

        raw_targets = metadata.get(
            "adaptive_quiz_targets",
            [],
        )

        if not isinstance(
            raw_targets,
            list,
        ):
            return []

        targets: list[tuple[str, float]] = []

        for item in raw_targets:

            if not isinstance(
                item,
                dict,
            ):
                continue

            concept_id = item.get(
                "concept_id",
            )

            score = item.get(
                "score",
            )

            if not isinstance(
                concept_id,
                str,
            ):
                continue

            if not isinstance(
                score,
                (int, float),
            ):
                continue

            targets.append(
                (
                    concept_id,
                    float(score),
                ),
            )

        targets.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        return targets

    @staticmethod
    def _prioritize_concepts(
        concept_ids: list[str],
        adaptive_targets: list[tuple[str, float]],
    ) -> list[str]:

        unique_concepts = list(
            dict.fromkeys(
                concept_ids,
            )
        )

        if not adaptive_targets:
            return unique_concepts

        target_rank = {
            concept_id: index
            for index, (
                concept_id,
                _,
            ) in enumerate(
                adaptive_targets,
            )
        }

        return sorted(
            unique_concepts,
            key=lambda concept_id: (
                target_rank.get(
                    concept_id,
                    len(target_rank),
                ),
                concept_id,
            ),
        )

    @staticmethod
    def _attach_target_metadata(
        action: AdaptiveTeachingAction,
        adaptive_targets: list[tuple[str, float]],
    ) -> None:

        if not adaptive_targets:
            return

        action.set_metadata(
            "adaptive_quiz_targets",
            [
                {
                    "concept_id": concept_id,
                    "score": score,
                }
                for concept_id, score
                in adaptive_targets
            ],
        )

        selected_target = next(
            (
                concept_id
                for concept_id, _
                in adaptive_targets
                if concept_id in action.focus_concepts
            ),
            None,
        )

        if selected_target is not None:
            action.set_metadata(
                "selected_quiz_target",
                selected_target,
            )