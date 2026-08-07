from __future__ import annotations

from pydantic import BaseModel, Field


class LearningProfile(BaseModel):
    """
    Describes the learner from an educational perspective.

    This object intentionally excludes authentication
    and personal account information.
    """

    current_level: str = ""

    target_level: str = ""

    interests: list[str] = Field(
        default_factory=list,
    )

    strengths: list[str] = Field(
        default_factory=list,
    )

    weaknesses: list[str] = Field(
        default_factory=list,
    )

    preferred_language: str = "vi"

    def add_interest(
        self,
        interest: str,
    ) -> None:

        if interest not in self.interests:
            self.interests.append(
                interest,
            )

    def add_strength(
        self,
        value: str,
    ) -> None:

        if value not in self.strengths:
            self.strengths.append(
                value,
            )

    def add_weakness(
        self,
        value: str,
    ) -> None:

        if value not in self.weaknesses:
            self.weaknesses.append(
                value,
            )