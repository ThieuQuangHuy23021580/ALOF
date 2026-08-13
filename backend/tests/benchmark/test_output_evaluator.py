from __future__ import annotations

from backend.benchmark.output_evaluator import (
    OutputEvaluator,
)
from backend.benchmark.result import (
    BenchmarkResult,
)
from backend.benchmark.scenario import (
    BenchmarkScenario,
)


def create_scenario() -> BenchmarkScenario:

    return BenchmarkScenario(
        id="python_explanation",
        name="Python Explanation",
        user_request="Explain Python.",
        component_ids=[
            "research",
            "mentor",
        ],
        expected_output="Lesson",
    )


def test_output_evaluator_accepts_valid_output():

    scenario = create_scenario()

    result = BenchmarkResult(
        scenario_id="python_explanation",
        approach="multi_agent",
        success=True,
        output="Python là ngôn ngữ lập trình cấp cao.",
    )

    assert (
        OutputEvaluator.evaluate(
            scenario,
            result,
        )
        is True
    )


def test_output_evaluator_rejects_missing_output():

    scenario = create_scenario()

    result = BenchmarkResult(
        scenario_id="python_explanation",
        approach="multi_agent",
        success=True,
        output=None,
    )

    assert (
        OutputEvaluator.evaluate(
            scenario,
            result,
        )
        is False
    )


def test_output_evaluator_rejects_empty_output():

    scenario = create_scenario()

    result = BenchmarkResult(
        scenario_id="python_explanation",
        approach="multi_agent",
        success=True,
        output="   ",
    )

    assert (
        OutputEvaluator.evaluate(
            scenario,
            result,
        )
        is False
    )


def test_output_evaluator_rejects_failed_result():

    scenario = create_scenario()

    result = BenchmarkResult(
        scenario_id="python_explanation",
        approach="multi_agent",
        success=False,
        output=None,
    )

    assert (
        OutputEvaluator.evaluate(
            scenario,
            result,
        )
        is False
    )