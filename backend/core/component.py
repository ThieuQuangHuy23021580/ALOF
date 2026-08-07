from __future__ import annotations

from abc import ABC, abstractmethod
from typing import final

from backend.core.component_context import ComponentContext
from backend.core.component_result import ComponentResult


class Component(ABC):
    """
    Base class for every executable component.

    Components are pure execution units.

    They never:
    - perform routing
    - execute another component
    - modify workflow topology

    They only transform ComponentContext
    into one ComponentResult.
    """

    component_id: str = ""

    name: str = ""

    description: str = ""

    version: str = "1.0.0"

    def __repr__(
        self,
    ) -> str:

        return (
            f"<Component {self.component_id}>"
        )

    @final
    def invoke(
        self,
        context: ComponentContext,
    ) -> ComponentResult:

        self.before_execute(
            context,
        )

        result = self.execute(
            context,
        )

        self.after_execute(
            context=context,
            result=result,
        )

        return result

    def before_execute(
        self,
        context: ComponentContext,
    ) -> None:

        return None

    @abstractmethod
    def execute(
        self,
        context: ComponentContext,
    ) -> ComponentResult:
        """
        Execute the component and produce exactly one ComponentResult.
        """
        raise NotImplementedError

    def after_execute(
        self,
        context: ComponentContext,
        result: ComponentResult,
    ) -> None:

        return None