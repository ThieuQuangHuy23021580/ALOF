
from __future__ import annotations

from typing import Any

from backend.application.runtime.runtime_context import (
    RuntimeContext,
)
from backend.domain.workflow.workflow_node import WorkflowNode

from .component_context import ComponentContext
from .dependency_context import DependencyContext


class ComponentContextBuilder:
    """
    Builds the ComponentContext required by a Component.

    Responsibilities
    ----------------
    - Collect dependency artifacts from parent nodes.
    - Inject runtime-level dependencies.
    - Create a ComponentContext.
    - Keep context construction outside the Runtime.
    """

    def __init__(
        self,
        dependencies: dict[str, Any] | None = None,
    ) -> None:

        self._dependencies = (
            dependencies.copy()
            if dependencies is not None
            else {}
        )

    def build(
        self,
        runtime: RuntimeContext,
        node: WorkflowNode,
    ) -> ComponentContext:

        inputs = self._build_inputs(
            runtime,
            node,
        )

        dependency_context = (
            self._build_dependency_context()
        )

        return ComponentContext(
            runtime=runtime,
            node=node,
            inputs=inputs,
            dependencies=dependency_context,
        )

    def _build_inputs(
        self,
        runtime: RuntimeContext,
        node: WorkflowNode,
    ) -> dict[str, Any]:

        inputs: dict[str, Any] = {}

        parents = runtime.workflow.parents(
            node.id,
        )

        for parent in parents:

            artifact = runtime.get_artifact(
                parent.id,
            )

            if artifact is not None:

                inputs[parent.id] = artifact

        return inputs

    def _build_dependency_context(
        self,
    ) -> DependencyContext:

        return DependencyContext(
            dependencies=self._dependencies.copy(),
        )

