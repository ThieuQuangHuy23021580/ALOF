from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class LearningInteraction(BaseModel):
    """
    Represents one observable learning interaction.

    An interaction is evidence used to update the
    learner model.
    """

    id: str = Field(
        default_factory=lambda: str(uuid4()),
    )

    learner_id: str

    question_id: str | None = None

    question: str = ""

    answer: str = ""

    correct: bool | None = None

    concept_ids: list[str] = Field(
        default_factory=list,
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
    )

    metadata: dict[str, object] = Field(
        default_factory=dict,
    )