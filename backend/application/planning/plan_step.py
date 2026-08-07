from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PlanStep(BaseModel):
    """
    Represents one logical step in an execution plan.
    """

    id: str

    component: str

    objective: str

    expected_output: str

    depends_on: list[str] = Field(
        default_factory=list,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    def add_dependency(
        self,
        step_id: str,
    ) -> None:

        if step_id not in self.depends_on:
            self.depends_on.append(
                step_id,
            )