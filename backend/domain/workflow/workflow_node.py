from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from backend.domain.learning.adaptive_teaching_action import (
    TeachingActionType,
    TeachingStrategy,
)


class WorkflowNode(BaseModel):
    """
    Runtime execution node.

    A WorkflowNode represents one executable component
    inside a workflow graph.

    It also preserves the adaptive teaching decision
    selected during planning.
    """

    id: str

    component_id: str

    objective: str

    expected_output: str = ""

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
    # Adaptive teaching
    # ======================================================

    def set_adaptive_action(
        self,
        action: TeachingActionType,
        strategy: TeachingStrategy,
        difficulty: str,
        focus_concepts: list[str] | None = None,
    ) -> None:
        """
        Set the adaptive teaching information
        for this workflow node.
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
        Return whether this workflow node contains
        an adaptive teaching decision.
        """

        return (
            self.action is not None
            and self.strategy is not None
        )

    def add_focus_concept(
        self,
        concept_id: str,
    ) -> None:

        if concept_id not in self.focus_concepts:
            self.focus_concepts.append(
                concept_id,
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