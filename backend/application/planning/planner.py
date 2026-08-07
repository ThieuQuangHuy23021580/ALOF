from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from .plan import Plan
from .planning_request import PlanningRequest


class Planner(ABC):
    """
    Generates a logical execution plan.

    A Planner decides WHAT should be done,
    but not HOW it will be executed.
    """

    @abstractmethod
    def plan(
        self,
        request: PlanningRequest,
    ) -> Plan:
        raise NotImplementedError