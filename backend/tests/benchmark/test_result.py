from __future__ import annotations

from backend.benchmark.result import (
    BenchmarkResult,
)


def test_benchmark_result_creation():

    result = BenchmarkResult(
        scenario_id="research_to_mentor",
        approach="multi_agent",
        success=True,
        output="Python Lesson",
    )

    assert (
        result.scenario_id
        == "research_to_mentor"
    )

    assert (
        result.approach
        == "multi_agent"
    )

    assert result.success is True

    assert (
        result.output
        == "Python Lesson"
    )

    assert result.metadata == {}


def test_benchmark_result_supports_failed_execution():

    result = BenchmarkResult(
        scenario_id="research_to_mentor",
        approach="multi_agent",
        success=False,
    )

    assert result.success is False

    assert result.output is None


def test_benchmark_result_supports_metadata():

    result = BenchmarkResult(
        scenario_id="research_to_mentor",
        approach="multi_agent",
        success=True,
        output="Python Lesson",
        metadata={
            "agent_count": 2,
            "execution_order": [
                "research",
                "mentor",
            ],
        },
    )

    assert (
        result.metadata["agent_count"]
        == 2
    )

    assert (
        result.metadata["execution_order"]
        == [
            "research",
            "mentor",
        ]
    )