from __future__ import annotations

from abc import ABC, abstractmethod

from backend.domain.student.student import Student

from .routing_result import RoutingResult


class Router(ABC):
    """
    Defines the routing contract.

    A router identifies the learner's intent and suggests
    candidate components. It does not create workflows
    or execution plans.
    """

    @abstractmethod
    def route(
        self,
        student: Student,
        message: str,
    ) -> RoutingResult:
        """
        Determine the learner's intent and candidate
        components for the given message.
        """
        raise NotImplementedError