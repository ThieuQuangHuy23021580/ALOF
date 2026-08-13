from __future__ import annotations

from backend.benchmark.report import BenchmarkReport
from backend.benchmark.result import BenchmarkResult
from backend.benchmark.comparison import BenchmarkComparison


def create_comparisons():

    return [
        BenchmarkComparison(
            single_agent=BenchmarkResult(
                scenario_id="scenario_1",
                approach="single_agent",
                success=True,
                output="single",
                metadata={
                    "duration": 2.0,
                    "llm_calls": 1,
                },
            ),
            multi_agent=BenchmarkResult(
                scenario_id="scenario_1",
                approach="multi_agent",
                success=True,
                output="multi",
                metadata={
                    "duration": 4.0,
                    "llm_calls": 3,
                },
            ),
        ),
        BenchmarkComparison(
            single_agent=BenchmarkResult(
                scenario_id="scenario_2",
                approach="single_agent",
                success=False,
                output="single",
                metadata={
                    "duration": 4.0,
                    "llm_calls": 1,
                },
            ),
            multi_agent=BenchmarkResult(
                scenario_id="scenario_2",
                approach="multi_agent",
                success=True,
                output="multi",
                metadata={
                    "duration": 6.0,
                    "llm_calls": 4,
                },
            ),
        ),
    ]


def test_benchmark_report_builds_summary():

    report = BenchmarkReport.build(
        create_comparisons(),
    )

    assert report.total_scenarios == 2

    assert (
        report.single_agent_success_rate
        == 0.5
    )

    assert (
        report.multi_agent_success_rate
        == 1.0
    )


def test_benchmark_report_calculates_average_duration():

    report = BenchmarkReport.build(
        create_comparisons(),
    )

    assert (
        report.single_agent_average_duration
        == 3.0
    )

    assert (
        report.multi_agent_average_duration
        == 5.0
    )


def test_benchmark_report_calculates_average_llm_calls():

    report = BenchmarkReport.build(
        create_comparisons(),
    )

    assert (
        report.single_agent_average_llm_calls
        == 1.0
    )

    assert (
        report.multi_agent_average_llm_calls
        == 3.5
    )


def test_empty_benchmark_report():

    report = BenchmarkReport.build(
        [],
    )

    assert report.total_scenarios == 0
    assert report.single_agent_success_rate == 0.0
    assert report.multi_agent_success_rate == 0.0
    assert report.comparisons == []