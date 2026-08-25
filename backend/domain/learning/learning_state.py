from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator

from backend.domain.knowledge.knowledge_state import (
    KnowledgeState,
)
from backend.domain.learning.learning_interaction import (
    LearningInteraction,
)


class LearningState(BaseModel):
    """
    Represents the learner's current adaptive learning state.

    LearningState contains the learner model used by
    routing, planning, execution and adaptation.
    """

    learner_id: str

    knowledge: dict[str, KnowledgeState] = Field(
        default_factory=dict,
    )

    interactions: list[LearningInteraction] = Field(
        default_factory=list,
    )

    progress: dict[str, float] = Field(
        default_factory=dict,
    )

    metadata: dict[str, object] = Field(
        default_factory=dict,
    )

    # ======================================================
    # Backward compatibility
    # ======================================================

    @model_validator(mode="before")
    @classmethod
    def normalize_legacy_knowledge(
        cls,
        data: Any,
    ) -> Any:
        """
        Normalize the old current_knowledge format
        into the new knowledge structure.
        """

        if not isinstance(data, dict):
            return data

        data = dict(data)

        legacy_knowledge = data.pop(
            "current_knowledge",
            None,
        )

        if legacy_knowledge is None:
            return data

        knowledge = dict(
            data.get(
                "knowledge",
                {},
            )
        )

        for concept_id, value in legacy_knowledge.items():

            if isinstance(
                value,
                KnowledgeState,
            ):
                knowledge[concept_id] = value
                continue

            state = KnowledgeState(
                concept_id=concept_id,
            )

            if isinstance(
                value,
                str,
            ):
                level_map = {
                    "unknown": 0.0,
                    "basic": 0.2,
                    "beginner": 0.2,
                    "intermediate": 0.5,
                    "understood": 0.8,
                    "advanced": 0.75,
                    "mastered": 0.95,
                }

                normalized = value.lower()

                if normalized in level_map:
                    state.update_mastery(
                        level_map[normalized],
                    )

                else:
                    # Free-form legacy knowledge such as
                    # "basic syntax" should be preserved.
                    state.metadata[
                        "legacy_label"
                    ] = value

            else:
                state.metadata[
                    "value"
                ] = value

            knowledge[concept_id] = state

        data["knowledge"] = knowledge

        return data

    # ======================================================
    # Backward-compatible Knowledge API
    # ======================================================

    @property
    def current_knowledge(
        self,
    ) -> dict[str, str]:
        """
        Backward-compatible view of knowledge.

        New code should use `knowledge`.
        """

        return {
            concept_id: self._knowledge_label(
                state,
            )
            for concept_id, state
            in self.knowledge.items()
        }

    @staticmethod
    def _knowledge_label(
        state: KnowledgeState,
    ) -> str:
        """
        Convert KnowledgeState into the legacy
        current_knowledge representation.

        The legacy API preserves the original labels
        such as:
            basic
            intermediate
            understood
            advanced
            mastered

        New code should use KnowledgeState.level directly.
        """

        legacy_label = state.metadata.get(
            "legacy_label",
        )

        if legacy_label is not None:
            return str(
                legacy_label,
            )

        if state.mastery == 0.2:
            return "basic"

        if state.mastery == 0.5:
            return "intermediate"

        if state.mastery == 0.8:
            return "understood"

        if state.mastery == 0.75:
            return "advanced"

        if state.mastery == 0.95:
            return "mastered"

        return state.level.value

    def update_knowledge(
        self,
        topic: str,
        knowledge: object,
    ) -> None:
        """
        Backward-compatible knowledge update API.

        New code should prefer update_mastery() or
        get_knowledge_state().
        """

        state = self.get_knowledge_state(
            topic,
        )

        if isinstance(
            knowledge,
            KnowledgeState,
        ):
            self.knowledge[topic] = knowledge
            return

        if isinstance(
            knowledge,
            str,
        ):
            level_map = {
                "unknown": 0.0,
                "basic": 0.2,
                "beginner": 0.2,
                "intermediate": 0.5,
                "understood": 0.8,
                "advanced": 0.75,
                "mastered": 0.95,
            }

            normalized = knowledge.lower()

            if normalized in level_map:

                state.update_mastery(
                    level_map[normalized],
                )

                # Remove any previous free-form label.
                state.metadata.pop(
                    "legacy_label",
                    None,
                )

            else:
                # Preserve free-form knowledge descriptions.
                state.metadata[
                    "legacy_label"
                ] = knowledge

            return

        state.metadata[
            "value"
        ] = knowledge

    def get_knowledge(
        self,
        topic: str,
        default: object = None,
    ) -> object:
        """
        Return backward-compatible knowledge value.
        """

        if topic not in self.knowledge:
            return default

        return self._knowledge_label(
            self.knowledge[topic],
        )

    # ======================================================
    # Knowledge State
    # ======================================================

    def get_knowledge_state(
        self,
        concept_id: str,
    ) -> KnowledgeState:
        """
        Return the KnowledgeState for a concept.

        Creates a default state when the concept does
        not yet exist.
        """

        if concept_id not in self.knowledge:

            self.knowledge[concept_id] = (
                KnowledgeState(
                    concept_id=concept_id,
                )
            )

        return self.knowledge[concept_id]

    def update_mastery(
        self,
        concept_id: str,
        mastery: float,
    ) -> None:
        """
        Update mastery for a knowledge concept.
        """

        state = self.get_knowledge_state(
            concept_id,
        )

        state.update_mastery(
            mastery,
        )

    # ======================================================
    # Interaction
    # ======================================================

    def add_interaction(
        self,
        interaction: LearningInteraction,
    ) -> None:
        """
        Add one learner interaction and update
        affected knowledge states.
        """

        self.interactions.append(
            interaction,
        )

        if interaction.correct is None:
            return

        for concept_id in interaction.concept_ids:

            state = self.get_knowledge_state(
                concept_id,
            )

            state.record_attempt(
                interaction.correct,
            )

    # ======================================================
    # Progress
    # ======================================================

    def update_progress(
        self,
        topic: str,
        value: float,
    ) -> None:
        """
        Update learning progress for a topic.
        """

        self.progress[topic] = value

    def get_progress(
        self,
        topic: str,
        default: float | None = None,
    ) -> float | None:
        """
        Get progress for a topic.
        """

        return self.progress.get(
            topic,
            default,
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
        Set learner metadata.
        """

        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default: object = None,
    ) -> object:
        """
        Get learner metadata.
        """

        return self.metadata.get(
            key,
            default,
        )