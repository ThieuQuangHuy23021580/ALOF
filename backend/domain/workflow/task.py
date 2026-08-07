from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from backend.core.component import Component


class LearningTask(BaseModel):
    """
    Atomic unit of work inside a Workflow.

    A task represents one execution of one Component.
    """

    id: str

    component: Component

    objective: str

    inputs: list[str] = Field(
        default_factory=list,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    def add_input(
        self,
        artifact_id: str,
    ) -> None:

        if artifact_id not in self.inputs:
            self.inputs.append(
                artifact_id,
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