from __future__ import annotations

import pytest

from backend.application.services.llm_service import (
    LLMService,
)


@pytest.mark.real_llm
def test_real_llm_service_tracks_stage_metrics():

    # ==========================================================
    # LLM Service
    # ==========================================================

    llm = LLMService()

    llm.reset_call_count()

    # ==========================================================
    # Routing call
    # ==========================================================

    routing_response = llm.generate(
        [
            {
                "role": "user",
                "content": (
                    "Classify this request: "
                    "compare REST and GraphQL."
                ),
            },
        ],
        stage="routing",
    )

    assert routing_response

    # ==========================================================
    # Planning call
    # ==========================================================

    planning_response = llm.generate(
        [
            {
                "role": "user",
                "content": (
                    "Create a sequential plan for "
                    "comparing REST and GraphQL."
                ),
            },
        ],
        stage="planning",
    )

    assert planning_response

    # ==========================================================
    # Runtime call
    # ==========================================================

    runtime_response = llm.generate(
        [
            {
                "role": "user",
                "content": (
                    "Explain one important difference "
                    "between REST and GraphQL."
                ),
            },
        ],
        stage="runtime",
    )

    assert runtime_response

    # ==========================================================
    # Basic metrics
    # ==========================================================

    assert llm.call_count == 3

    metrics = llm.call_metrics

    assert len(metrics) == 3

    # ==========================================================
    # Stage assertions
    # ==========================================================

    assert metrics[0].stage == "routing"

    assert metrics[1].stage == "planning"

    assert metrics[2].stage == "runtime"

    # ==========================================================
    # Token assertions
    # ==========================================================

    for metric in metrics:

        assert metric.input_tokens > 0

        assert metric.output_tokens > 0

        assert metric.total_tokens > 0

        assert (
            metric.total_tokens
            == (
                metric.input_tokens
                + metric.output_tokens
            )
        )

        assert metric.duration > 0

    # ==========================================================
    # Stage aggregation
    # ==========================================================

    assert (
        len(
            llm.metrics_by_stage(
                "routing",
            )
        )
        == 1
    )

    assert (
        len(
            llm.metrics_by_stage(
                "planning",
            )
        )
        == 1
    )

    assert (
        len(
            llm.metrics_by_stage(
                "runtime",
            )
        )
        == 1
    )

    # ==========================================================
    # Routing
    # ==========================================================

    routing_tokens = (
        llm.total_tokens_by_stage(
            "routing",
        )
    )

    assert routing_tokens > 0

    # ==========================================================
    # Planning
    # ==========================================================

    planning_tokens = (
        llm.total_tokens_by_stage(
            "planning",
        )
    )

    assert planning_tokens > 0

    # ==========================================================
    # Runtime
    # ==========================================================

    runtime_tokens = (
        llm.total_tokens_by_stage(
            "runtime",
        )
    )

    assert runtime_tokens > 0

    # ==========================================================
    # Total
    # ==========================================================

    assert (
        llm.total_tokens
        == (
            routing_tokens
            + planning_tokens
            + runtime_tokens
        )
    )

    # ==========================================================
    # Benchmark output
    # ==========================================================

    print(
        "\n"
        "=============================================="
    )

    print(
        "       LLM STAGE METRICS TEST"
    )

    print(
        "=============================================="
    )

    for stage in (
        "routing",
        "planning",
        "runtime",
    ):

        stage_metrics = (
            llm.metrics_by_stage(
                stage,
            )
        )

        print(
            f"\n[{stage.upper()}]"
        )

        print(
            f"Calls: "
            f"{len(stage_metrics)}"
        )

        print(
            f"Input tokens: "
            f"{llm.input_tokens_by_stage(stage)}"
        )

        print(
            f"Output tokens: "
            f"{llm.output_tokens_by_stage(stage)}"
        )

        print(
            f"Total tokens: "
            f"{llm.total_tokens_by_stage(stage)}"
        )

        print(
            f"Duration: "
            f"{llm.duration_by_stage(stage):.3f}s"
        )

    print(
        "\n[TOTAL]"
    )

    print(
        f"Calls: "
        f"{llm.call_count}"
    )

    print(
        f"Input tokens: "
        f"{llm.total_input_tokens}"
    )

    print(
        f"Output tokens: "
        f"{llm.total_output_tokens}"
    )

    print(
        f"Total tokens: "
        f"{llm.total_tokens}"
    )

    print(
        f"Duration: "
        f"{llm.total_duration:.3f}s"
    )

    print(
        "=============================================="
    )