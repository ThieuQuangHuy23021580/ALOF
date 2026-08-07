from __future__ import annotations

from enum import StrEnum


class ArtifactType(StrEnum):
    """
    Built-in artifact types of ALOF.
    """

    RESPONSE = "response"

    LESSON = "lesson"

    SUMMARY = "summary"

    ROADMAP = "roadmap"

    QUIZ = "quiz"

    FLASHCARD = "flashcard"


class ArtifactTypes:
    """
    Artifact type helper.
    """

    @classmethod
    def values(
        cls,
    ) -> set[str]:

        return {
            artifact_type.value
            for artifact_type in ArtifactType
        }

    @classmethod
    def exists(
        cls,
        value: str,
    ) -> bool:

        return value in cls.values()