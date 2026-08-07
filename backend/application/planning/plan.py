from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .plan_step import PlanStep


class Plan(BaseModel):
    """
    Logical execution plan produced by a Planner.
    """

    steps: list[PlanStep] = Field(
        default_factory=list,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    def add_step(
        self,
        step: PlanStep,
    ) -> None:

        self.steps.append(
            step,
        )

    def get_step(
        self,
        step_id: str,
    ) -> PlanStep | None:

        for step in self.steps:

            if step.id == step_id:
                return step

        return None