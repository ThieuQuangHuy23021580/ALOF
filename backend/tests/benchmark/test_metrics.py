from __future__ import annotations

from backend.benchmark.metrics import (
    BenchmarkMetrics,
)


def test_benchmark_metrics_creation():

    metrics = BenchmarkMetrics(
        duration=2.5,
        llm_calls=2,
        success=True,
    )

    assert (
        metrics.duration
        == 2.5
    )

    assert (
        metrics.llm_calls
        == 2
    )

    assert metrics.success is True

    assert (
        metrics.input_tokens
        is None
    )

    assert (
        metrics.output_tokens
        is None
    )

    assert (
        metrics.total_tokens
        is None
    )


def test_benchmark_metrics_supports_token_usage():

    metrics = BenchmarkMetrics(
        duration=3.2,
        llm_calls=2,
        success=True,
        input_tokens=500,
        output_tokens=300,
        total_tokens=800,
    )

    assert (
        metrics.input_tokens
        == 500
    )

    assert (
        metrics.output_tokens
        == 300
    )

    assert (
        metrics.total_tokens
        == 800
    )


def test_benchmark_metrics_supports_failed_execution():

    metrics = BenchmarkMetrics(
        duration=1.1,
        llm_calls=1,
        success=False,
    )

    assert metrics.success is False

    assert (
        metrics.llm_calls
        == 1
    )