from __future__ import annotations

from typing import List

from backend.application.runtime.runtime_context import RuntimeContext
from backend.core.component import Component
from backend.domain.artifact.artifact import Artifact
from backend.domain.workflow.workflow import Workflow
from backend.domain.workflow.task import LearningTask


class Executor:
    """
    Runtime engine of ALOF.

    Responsibilities
    ----------------
    - Execute a workflow.
    - Invoke components.
    - Collect artifacts.

    Executor never performs routing,
    planning or dependency resolution.
    """

    def execute(
        self,
        workflow: Workflow,
        context: RuntimeContext,
    ) -> list[Artifact]:

        artifacts: list[Artifact] = []

        for task in workflow.tasks:

            artifact = self.execute_task(
                task=task,
                context=context,
            )

            artifacts.append(
                artifact,
            )

        return artifacts

    def execute_task(
        self,
        task: LearningTask,
        context: RuntimeContext,
    ) -> Artifact:

        component = self._resolve_component(
            task,
        )

        artifact = component.invoke(
            context,
        )

        context.add_artifact(
            artifact,
        )

        return artifact

    def _resolve_component(
        self,
        task: LearningTask,
    ) -> Component:

        return task.component