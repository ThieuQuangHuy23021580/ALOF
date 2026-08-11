
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from backend.application.runtime.runtime_context import RuntimeContext
from backend.domain.workflow.workflow_node import WorkflowNode

from .dependency_context import DependencyContext


class ComponentContext(BaseModel):
    """
    Execution context passed to a Component.

    Contains:
    - Runtime state.
    - Current workflow node.
    - Component inputs.
    - Runtime dependencies.
    - Component metadata.

    Components should access execution data only through
    this context instead of depending directly on Runtime.
    """

    runtime: RuntimeContext

    node: WorkflowNode

    inputs: dict[str, Any] = Field(
        default_factory=dict,
    )

    dependencies: DependencyContext = Field(
        default_factory=DependencyContext,
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

    def get_dependency(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.dependencies.get(
            key,
            default,
        )

    def has_dependency(
        self,
        key: str,
    ) -> bool:

        return self.dependencies.has(
            key,
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

