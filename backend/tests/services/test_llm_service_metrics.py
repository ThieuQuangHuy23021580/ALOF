from __future__ import annotations

import pytest

from backend.application.services.llm_service import (
    LLMService,
)


@pytest.mark.real_llm
def test_real_llm_service_collects_usage_metrics():

    # ==========================================================
    # LLM Service
    # ==========================================================

    llm = LLMService()

    llm.reset_call_count()

    # ==========================================================
    # Real LLM call
    # ==========================================================

    response = llm.generate(
        "Explain REST API in one short paragraph.",
    )

    # ==========================================================
    # Basic response
    # ==========================================================

    assert response is not None

    # ==========================================================
    # Call count
    # ==========================================================

    assert llm.call_count == 1

    # ==========================================================
    # Metrics
    # ==========================================================

    metrics = llm.call_metrics

    assert len(metrics) == 1

    metric = metrics[0]

    assert metric.duration > 0

    # ==========================================================
    # Token usage
    # ==========================================================

    print(
        "\n"
        "=============================================="
    )

    print(
        "      LLM USAGE INSTRUMENTATION TEST"
    )

    print(
        "=============================================="
    )

    print(
        f"Call count: "
        f"{llm.call_count}"
    )

    print(
        f"Input tokens: "
        f"{metric.input_tokens}"
    )

    print(
        f"Output tokens: "
        f"{metric.output_tokens}"
    )

    print(
        f"Total tokens: "
        f"{metric.total_tokens}"
    )

    print(
        f"Duration: "
        f"{metric.duration:.3f}s"
    )

    print(
        f"Aggregated input tokens: "
        f"{llm.total_input_tokens}"
    )

    print(
        f"Aggregated output tokens: "
        f"{llm.total_output_tokens}"
    )

    print(
        f"Aggregated total tokens: "
        f"{llm.total_tokens}"
    )

    print(
        "=============================================="
    )

    # ==========================================================
    # Aggregation consistency
    # ==========================================================

    assert (
        llm.total_input_tokens
        == metric.input_tokens
    )

    assert (
        llm.total_output_tokens
        == metric.output_tokens
    )

    assert (
        llm.total_tokens
        == metric.total_tokens
    )