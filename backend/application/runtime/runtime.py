from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.application.runtime.runtime_context import RuntimeContext
from backend.application.runtime.runtime_result import RuntimeResult


class Runtime(ABC):
    """
    Executes a Workflow using a scheduling strategy.

    Runtime is responsible for driving the execution loop.
    It delegates scheduling and component execution to
    dedicated collaborators.
    """

    @abstractmethod
    def run(
        self,
        context: RuntimeContext,
    ) -> RuntimeResult:
        raise NotImplementedError