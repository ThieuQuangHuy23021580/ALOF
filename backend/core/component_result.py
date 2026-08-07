from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ComponentResult(BaseModel):
    """
    Standard runtime result produced by a Component.

    The artifact can be any domain object
    (LessonArtifact, QuizArtifact, ResearchArtifact, ...).
    """

    artifact: Any

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

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