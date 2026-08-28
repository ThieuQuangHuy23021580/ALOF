
from __future__ import annotations

from typing import Any

from backend.application.runtime.runtime import Runtime
from backend.application.runtime.runtime_context import RuntimeContext
from backend.application.runtime.runtime_result import RuntimeResult
from backend.application.runtime.sequential_scheduler import (
    SequentialScheduler,
)

from backend.core.component_context_builder import (
    ComponentContextBuilder,
)
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
    - Resolve Components through ComponentRegistry.
    - Build ComponentContext through ComponentContextBuilder.
    - Inject runtime-level dependencies into ComponentContext.
    - Execute Components.
    - Track execution timeline.
    - Update runtime state.

    The Runtime does not construct ComponentContext
    details directly.
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

        self._context_builder = (
            ComponentContextBuilder(
                dependencies=self._dependencies,
            )
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
                    )

                    component_context = (
                        self._context_builder.build(
                            runtime=context,
                            node=node,
                        )
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
            learning_state=context.learning_state,
            adaptive_learning=context.adaptive_learning,
        )

