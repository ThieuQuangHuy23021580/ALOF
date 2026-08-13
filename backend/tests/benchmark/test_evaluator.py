from __future__ import annotations

from backend.benchmark.evaluator import (
    TaskSuccessEvaluator,
)
from backend.benchmark.result import (
    BenchmarkResult,
)


def test_task_success_evaluator_accepts_successful_result():

    result = BenchmarkResult(
        scenario_id="python_explanation",
        approach="multi_agent",
        success=True,
        output="Python Lesson",
    )

    assert (
        TaskSuccessEvaluator.evaluate(
            result,
        )
        is True
    )


def test_task_success_evaluator_rejects_failed_result():

    result = BenchmarkResult(
        scenario_id="python_explanation",
        approach="multi_agent",
        success=False,
    )

    assert (
        TaskSuccessEvaluator.evaluate(
            result,
        )
        is False
    )