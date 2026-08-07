from __future__ import annotations

from backend.application.runtime.runtime_context import RuntimeContext
from backend.domain.workflow.workflow_node import WorkflowNode

from .scheduler import Scheduler


class SequentialScheduler(
    Scheduler,
):
    """
    Scheduler for sequential workflows.

    A node is executable when:
    - it has not been executed.
    - every parent node has completed.
    """

    def next(
        self,
        context: RuntimeContext,
    ) -> list[WorkflowNode]:

        workflow = context.workflow

        ready: list[WorkflowNode] = []

        for node in workflow.nodes:

            if context.has_artifact(
                node.id,
            ):
                continue

            parents = workflow.parents(
                node.id,
            )

            if all(
                context.has_artifact(
                    parent.id,
                )
                for parent in parents
            ):
                ready.append(
                    node,
                )

        return ready