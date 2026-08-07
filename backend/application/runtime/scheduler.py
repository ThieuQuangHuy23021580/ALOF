from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.application.runtime.runtime_context import RuntimeContext
from backend.domain.workflow.workflow_node import WorkflowNode


class Scheduler(ABC):
    """
    Selects the next executable WorkflowNode(s).

    Scheduler is responsible only for scheduling.
    It never executes components.
    """

    @abstractmethod
    def next(
        self,
        context: RuntimeContext,
    ) -> list[WorkflowNode]:
        """
        Returns all executable nodes at the current runtime state.
        """
        raise NotImplementedError