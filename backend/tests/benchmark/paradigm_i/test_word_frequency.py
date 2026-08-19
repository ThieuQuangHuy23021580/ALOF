from __future__ import annotations

import os
from pathlib import Path

from backend.benchmark.paradigms.paradigm_i.word_frequency import (
    WordFrequencyBenchmarkRunner,
)
from backend.benchmark.silo_adapter import (
    SILOBenchAdapter,
)
from backend.core.component_bootstrap import (
    register_components,
)


def test_alof_silo_word_frequency_with_real_llm():

    register_components()

    silo_root = os.environ[
        "SILO_BENCH_ROOT"
    ]

    task_file = (
        Path(silo_root)
        / "benchmarks"
        / "I-02_n2.json"
    )

    scenario = SILOBenchAdapter.load(
        task_file,
    )

    runner = WordFrequencyBenchmarkRunner()

    result = runner.run(
        scenario,
    )

    print()
    print("=" * 60)
    print(
        "ALOF × SILO-BENCH × REAL LLM"
    )
    print("=" * 60)

    print(
        f"scenario_id: "
        f"{result.scenario_id}"
    )

    print(
        f"scenario_name: "
        f"{result.scenario_name}"
    )

    print(
        f"success: "
        f"{result.success}"
    )

    print(
        f"total_count: "
        f"{result.details['total_count']}"
    )

    print(
        f"expected: "
        f"{result.details['expected']}"
    )

    print(
        f"local_counts: "
        f"{result.details['local_counts']}"
    )

    print(
        f"agent_count: "
        f"{result.agent_count}"
    )

    print(
        f"component_calls: "
        f"{result.component_calls}"
    )

    print(
        f"llm_calls: "
        f"{result.llm_calls}"
    )

    print(
        f"input_tokens: "
        f"{result.input_tokens}"
    )

    print(
        f"output_tokens: "
        f"{result.output_tokens}"
    )

    print(
        f"total_tokens: "
        f"{result.total_tokens}"
    )

    print()
    print(
        "----- M5.4 Communication -----"
    )

    print(
        f"communication_messages: "
        f"{result.communication_messages}"
    )

    print(
        f"optimal_message_count: "
        f"{result.details['optimal_message_count']}"
    )

    print(
        f"rounds: "
        f"{result.rounds}"
    )

    print(
        f"communication_redundancy_ratio: "
        f"{result.metrics['communication_redundancy_ratio']:.4f}"
    )

    print(
        f"topological_fidelity: "
        f"{result.metrics['topological_fidelity']:.4f}"
    )

    print(
        f"communication_trace: "
        f"{result.details['communication_trace']}"
    )

    print()
    print(
        f"duration_seconds: "
        f"{result.duration_seconds:.4f}"
    )

    print("=" * 60)

    # ======================================================
    # Correctness
    # ======================================================

    assert result.success is True

    assert (
        result.details["total_count"]
        == 14
    )

    assert (
        result.details["local_counts"]
        == [7, 7]
    )

    # ======================================================
    # Real LLM
    # ======================================================

    assert result.llm_calls == 2

    assert result.total_tokens > 0

    # ======================================================
    # Communication
    # ======================================================

    assert (
        result.communication_messages
        == 2
    )

    assert (
        result.details["optimal_message_count"]
        == 2
    )

    assert result.rounds == 2

    assert (
        result.metrics[
            "communication_redundancy_ratio"
        ]
        == 1.0
    )

    assert (
        result.metrics[
            "topological_fidelity"
        ]
        == 1.0
    )

    assert (
        result.details["communication_trace"]
        == [
            {
                "sender": 1,
                "receiver": 0,
                "round": 1,
                "message_type": "local_count",
                "payload": 7,
            },
            {
                "sender": 0,
                "receiver": 1,
                "round": 2,
                "message_type": "global_count",
                "payload": 14,
            },
        ]
    )