from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from backend.benchmark.result import BenchmarkResult
from backend.benchmark.scenario import BenchmarkScenario


class BenchmarkRunner(ABC):
    """
    Contract for benchmark execution.

    A BenchmarkRunner executes one BenchmarkScenario
    and returns a standardized BenchmarkResult.
    """

    @abstractmethod
    def run(
        self,
        scenario: BenchmarkScenario,
    ) -> BenchmarkResult:
        """
        Execute one benchmark scenario.
        """

        raise NotImplementedError