from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class LearningState(BaseModel):
    """
    Represents the learner's current learning state.
    """

    learner_id: str

    current_knowledge: dict[str, Any] = Field(
        default_factory=dict,
    )

    progress: dict[str, float] = Field(
        default_factory=dict,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    # ======================================================
    # Knowledge
    # ======================================================

    def update_knowledge(
        self,
        topic: str,
        knowledge: Any,
    ) -> None:

        self.current_knowledge[topic] = knowledge

    def get_knowledge(
        self,
        topic: str,
        default: Any = None,
    ) -> Any:

        return self.current_knowledge.get(
            topic,
            default,
        )

    # ======================================================
    # Progress
    # ======================================================

    def update_progress(
        self,
        topic: str,
        value: float,
    ) -> None:

        self.progress[topic] = value

    def get_progress(
        self,
        topic: str,
        default: float | None = None,
    ) -> float | None:

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
        value: Any,
    ) -> None:

        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.metadata.get(
            key,
            default,
        )