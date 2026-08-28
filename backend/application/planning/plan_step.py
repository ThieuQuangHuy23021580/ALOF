from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from backend.domain.learning.adaptive_teaching_action import (
    TeachingActionType,
    TeachingStrategy,
)


class PlanStep(BaseModel):
    """
    Represents one logical step in an execution plan.

    A PlanStep describes both:

    - what should be executed;
    - how the learner should be taught.

    Adaptive teaching information is derived from
    the domain-level AdaptiveTeachingAction.
    """

    id: str

    component: str

    objective: str

    expected_output: str

    depends_on: list[str] = Field(
        default_factory=list,
    )

    # ======================================================
    # Adaptive teaching
    # ======================================================

    action: TeachingActionType | None = None

    strategy: TeachingStrategy | None = None

    difficulty: str | None = None

    focus_concepts: list[str] = Field(
        default_factory=list,
    )

    # ======================================================
    # Metadata
    # ======================================================

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    # ======================================================
    # Dependencies
    # ======================================================

    def add_dependency(
        self,
        step_id: str,
    ) -> None:

        if step_id not in self.depends_on:
            self.depends_on.append(
                step_id,
            )

    # ======================================================
    # Adaptive teaching
    # ======================================================

    def add_focus_concept(
        self,
        concept_id: str,
    ) -> None:

        if concept_id not in self.focus_concepts:
            self.focus_concepts.append(
                concept_id,
            )

    def set_adaptive_action(
        self,
        action: TeachingActionType,
        strategy: TeachingStrategy,
        difficulty: str,
        focus_concepts: list[str] | None = None,
    ) -> None:
        """
        Set the adaptive teaching information
        for this plan step.
        """

        self.action = action
        self.strategy = strategy
        self.difficulty = difficulty

        if focus_concepts is not None:
            self.focus_concepts = list(
                dict.fromkeys(
                    focus_concepts,
                )
            )

    @property
    def has_adaptive_action(self) -> bool:
        """
        Return whether this plan step contains
        an adaptive teaching decision.
        """

        return (
            self.action is not None
            and self.strategy is not None
        )