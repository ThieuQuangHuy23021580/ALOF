from __future__ import annotations

from backend.core.component import Component
from backend.core.component_context import ComponentContext
from backend.core.component_executor import ComponentExecutor
from backend.core.component_result import ComponentResult


class DefaultComponentExecutor(
    ComponentExecutor,
):
    """
    Default synchronous ComponentExecutor.

    Responsibilities
    ----------------
    - Track component execution lifecycle.
    - Invoke a Component.
    - Return its ComponentResult.
    - Persist Artifact into RuntimeContext.
    - Do not perform scheduling, routing or retries.
    """

    def execute(
        self,
        component: Component,
        context: ComponentContext,
    ) -> ComponentResult:

        runtime = context.runtime

        runtime.start_component_execution(
            node_id=context.node.id,
            component_id=component.component_id,
        )

        try:

            result = component.invoke(
                context,
            )

            runtime.add_artifact(
                node_id=context.node.id,
                artifact=result.artifact,
            )

            runtime.complete_component_execution(
                node_id=context.node.id,
            )

            return result

        except Exception as exc:

            runtime.fail_component_execution(
                node_id=context.node.id,
                error=str(exc),
            )

            raise