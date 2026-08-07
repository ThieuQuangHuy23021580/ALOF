from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.application.planning.plan import Plan
from backend.domain.workflow.workflow import Workflow


class WorkflowBuilder(ABC):
    """
    Converts a logical Plan into an executable Workflow.

    Planner decides WHAT to execute.
    WorkflowBuilder decides HOW to represent it for runtime.
    """

    @abstractmethod
    def build(
        self,
        plan: Plan,
    ) -> Workflow:
        raise NotImplementedError