from __future__ import annotations

from typing import Any

from backend.application.runtime.runtime import Runtime
from backend.application.runtime.runtime_context import RuntimeContext
from backend.application.runtime.runtime_result import RuntimeResult
from backend.application.runtime.sequential_scheduler import (
    SequentialScheduler,
)

from backend.core.component_context import ComponentContext
from backend.core.component_executor import ComponentExecutor
from backend.core.component_registry import ComponentRegistry
from backend.core.default_component_executor import (
    DefaultComponentExecutor,
)
from backend.core.execution_status import ExecutionStatus


class SequentialRuntime(Runtime):
    """
    Default runtime for sequential workflows.

    Responsibilities
    ----------------
    - Ask Scheduler for executable nodes.
    - Create ComponentContext.
    - Resolve Components through ComponentRegistry.
    - Inject runtime-level dependencies.
    - Execute Components.
    - Track execution timeline.
    - Update runtime state.
    """

    def __init__(
        self,
        scheduler: SequentialScheduler | None = None,
        executor: ComponentExecutor | None = None,
        dependencies: dict[str, Any] | None = None,
    ) -> None:

        self._scheduler = (
            scheduler
            if scheduler is not None
            else SequentialScheduler()
        )

        self._executor = (
            executor
            if executor is not None
            else DefaultComponentExecutor()
        )

        self._dependencies = (
            dependencies.copy()
            if dependencies is not None
            else {}
        )

    def run(
        self,
        context: RuntimeContext,
    ) -> RuntimeResult:

        context.state = ExecutionStatus.RUNNING

        context.start_execution()

        try:

            while True:

                ready_nodes = self._scheduler.next(
                    context,
                )

                if not ready_nodes:
                    break

                for node in ready_nodes:

                    context.set_current_node(
                        node.id,
                    )

                    context.add_execution_step(
                        node.id,
                    )

                    component = ComponentRegistry.create(
                        node.component_id,
                        **self._dependencies,
                    )

                    component_context = ComponentContext(
                        runtime=context,
                        node=node,
                        inputs=self._build_component_inputs(
                            context,
                            node,
                        ),
                    )

                    self._executor.execute(
                        component=component,
                        context=component_context,
                    )

            context.state = (
                ExecutionStatus.COMPLETED
            )

        except Exception as exc:

            context.state = (
                ExecutionStatus.FAILED
            )

            context.set_metadata(
                "error",
                str(exc),
            )

            raise

        finally:

            context.set_current_node(
                None,
            )

            context.finish_execution()

        return self.build_result(
            context,
        )

    def build_result(
        self,
        context: RuntimeContext,
    ) -> RuntimeResult:

        final_artifact = None

        if context.execution_order:

            last_node_id = (
                context.execution_order[-1]
            )

            final_artifact = (
                context.get_artifact(
                    last_node_id,
                )
            )

        return RuntimeResult(
            status=context.state,
            artifacts=context.artifacts,
            final_artifact=final_artifact,
            execution_order=context.execution_order,
            duration=context.execution_duration(),
            metadata=context.metadata,
        )

    def _build_component_inputs(
        self,
        context: RuntimeContext,
        node,
    ) -> dict[str, Any]:

        inputs: dict[str, Any] = {}

        parents = context.workflow.parents(
            node.id,
        )

        for parent in parents:

            artifact = context.get_artifact(
                parent.id,
            )

            if artifact is not None:

                inputs[parent.id] = artifact

        return inputs