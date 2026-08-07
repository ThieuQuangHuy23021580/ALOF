from __future__ import annotations

from pydantic import BaseModel, Field


class LearningPreference(BaseModel):
    """
    Represents how the learner prefers to study.

    Preferences are user-configurable settings used by
    the orchestrator to personalize learning workflows.
    """

    preferred_outputs: list[str] = Field(
        default_factory=list,
    )

    preferred_difficulty: str = "adaptive"

    preferred_pace: str = "adaptive"

    session_duration_minutes: int = 30

    include_examples: bool = True

    include_quiz: bool = True

    include_flashcards: bool = True

    include_summary: bool = True

    def add_output(
        self,
        output: str,
    ) -> None:

        if output not in self.preferred_outputs:
            self.preferred_outputs.append(
                output,
            )

    def remove_output(
        self,
        output: str,
    ) -> None:

        if output in self.preferred_outputs:
            self.preferred_outputs.remove(
                output,
            )