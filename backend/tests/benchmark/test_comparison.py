from __future__ import annotations

from backend.benchmark.comparison import (
    BenchmarkComparison,
)
from backend.benchmark.result import (
    BenchmarkResult,
)


def create_single_result() -> BenchmarkResult:

    return BenchmarkResult(
        scenario_id="python_explanation",
        approach="single_agent",
        success=True,
        output="Python explanation.",
        metadata={
            "duration": 1.0,
            "llm_calls": 1,
        },
    )


def create_multi_result() -> BenchmarkResult:

    return BenchmarkResult(
        scenario_id="python_explanation",
        approach="multi_agent",
        success=True,
        output="Python lesson.",
        metadata={
            "duration": 2.0,
            "llm_calls": 2,
        },
    )


def test_comparison_contains_both_results():

    comparison = BenchmarkComparison(
        single_agent=create_single_result(),
        multi_agent=create_multi_result(),
    )

    assert (
        comparison.single_agent.approach
        == "single_agent"
    )

    assert (
        comparison.multi_agent.approach
        == "multi_agent"
    )


def test_comparison_reports_success():

    comparison = BenchmarkComparison(
        single_agent=create_single_result(),
        multi_agent=create_multi_result(),
    )

    assert comparison.single_success is True
    assert comparison.multi_success is True


def test_comparison_reports_duration():

    comparison = BenchmarkComparison(
        single_agent=create_single_result(),
        multi_agent=create_multi_result(),
    )

    assert comparison.single_duration == 1.0
    assert comparison.multi_duration == 2.0


def test_comparison_reports_llm_calls():

    comparison = BenchmarkComparison(
        single_agent=create_single_result(),
        multi_agent=create_multi_result(),
    )

    assert comparison.single_llm_calls == 1
    assert comparison.multi_llm_calls == 2


def test_comparison_calculates_duration_difference():

    comparison = BenchmarkComparison(
        single_agent=create_single_result(),
        multi_agent=create_multi_result(),
    )

    assert comparison.duration_difference == 1.0


def test_multi_agent_success_advantage():

    single = BenchmarkResult(
        scenario_id="test",
        approach="single_agent",
        success=False,
        output=None,
        metadata={
            "duration": 1.0,
            "llm_calls": 1,
        },
    )

    multi = BenchmarkResult(
        scenario_id="test",
        approach="multi_agent",
        success=True,
        output="valid output",
        metadata={
            "duration": 2.0,
            "llm_calls": 2,
        },
    )

    comparison = BenchmarkComparison(
        single_agent=single,
        multi_agent=multi,
    )

    assert (
        comparison.multi_agent_success_advantage
        is True
    )