from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from .component import Component
from .component_context import ComponentContext
from .component_result import ComponentResult


class ComponentExecutor(ABC):
    """
    Executes a Component.

    The executor is responsible for invoking the component,
    but it does not know any business logic.
    """

    @abstractmethod
    def execute(
        self,
        component: Component,
        context: ComponentContext,
    ) -> ComponentResult:
        """
        Execute one component and return its runtime result.
        """
        raise NotImplementedError