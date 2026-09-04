from __future__ import annotations

from enum import StrEnum


class KnowledgeLevel(StrEnum):
    """
    Represents learner mastery over a knowledge node.
    """

    BEGINNER = "beginner"

    INTERMEDIATE = "intermediate"

    ADVANCED = "advanced"

