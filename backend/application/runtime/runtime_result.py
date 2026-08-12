from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from backend.core.execution_status import ExecutionStatus
from backend.domain.artifact.artifact import Artifact
from backend.domain.learning.learning_state import (
    LearningState,
)

class RuntimeResult(BaseModel):
    """
    Final output produced after workflow execution.
    """

    status: ExecutionStatus

    artifacts: dict[str, Artifact] = Field(
        default_factory=dict,
    )

    final_artifact: Artifact | None = None

    execution_order: list[str] = Field(
        default_factory=list,
    )

    duration: float | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    learning_state: LearningState | None = None

    def add_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.metadata[key] = value

    @property
    def execution_count(self) -> int:
        return len(self.execution_order)


    @property
    def artifact_count(self) -> int:
        return len(self.artifacts)


    @property
    def last_node_id(self) -> str | None:
        if not self.execution_order:
            return None

        return self.execution_order[-1]