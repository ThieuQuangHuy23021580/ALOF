from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from backend.application.runtime.runtime_context import RuntimeContext
from backend.domain.workflow.workflow_node import WorkflowNode


class ComponentContext(BaseModel):
    """
    Execution context passed to a Component.
    """

    runtime: RuntimeContext

    node: WorkflowNode

    inputs: dict[str, Any] = Field(
        default_factory=dict,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    def get_input(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.inputs.get(
            key,
            default,
        )

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.metadata[key] = value