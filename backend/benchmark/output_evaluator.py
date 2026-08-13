from __future__ import annotations

from backend.benchmark.result import BenchmarkResult
from backend.benchmark.scenario import BenchmarkScenario


class OutputEvaluator:
    """
    Deterministic evaluator for benchmark outputs.
    """

    @staticmethod
    def evaluate(
        scenario: BenchmarkScenario,
        result: BenchmarkResult,
    ) -> bool:

        if not result.success:
            return False

        if result.output is None:
            return False

        if not result.output.strip():
            return False

        return True