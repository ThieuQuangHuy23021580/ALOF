from __future__ import annotations

from backend.benchmark.result import BenchmarkResult


class TaskSuccessEvaluator:
    """
    Deterministic evaluator for benchmark task execution.
    """

    @staticmethod
    def evaluate(
        result: BenchmarkResult,
    ) -> bool:

        return result.success