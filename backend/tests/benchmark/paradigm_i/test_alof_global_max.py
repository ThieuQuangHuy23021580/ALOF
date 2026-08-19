from __future__ import annotations

import os
from pathlib import Path

from backend.benchmark.paradigms.paradigm_i.global_max.runner import (
    ALOFBenchmarkRunner,
)
from backend.benchmark.silo_adapter import (
    SILOBenchAdapter,
)
from backend.core.component_bootstrap import (
    register_components,
)


def test_alof_silo_global_max_with_real_llm():

    # ======================================================
    # Bootstrap
    # ======================================================

    register_components()

    # ======================================================
    # Load SILO-BENCH scenario
    # ======================================================

    silo_root = os.environ[
        "SILO_BENCH_ROOT"
    ]

    task_file = (
        Path(silo_root)
        / "benchmarks"
        / "I-01_n2.json"
    )

    scenario = SILOBenchAdapter.load(
        task_file,
    )

    # ======================================================
    # Run ALOF
    # ======================================================

    runner = ALOFBenchmarkRunner()

    result = runner.run(
        scenario,
    )

    # ======================================================
    # Extract M5 communication metrics
    # ======================================================

    communication_messages = (
        result.communication_messages
    )

    rounds = result.rounds

    communication_redundancy_ratio = (
        result.details[
            "communication_redundancy_ratio"
        ]
    )

    topological_fidelity = (
        result.details[
            "topological_fidelity"
        ]
    )

    communication_trace = (
        result.details[
            "communication_trace"
        ]
    )

    optimal_message_count = (
        result.details[
            "optimal_message_count"
        ]
    )

    # ======================================================
    # Output
    # ======================================================

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
        f"global_max: "
        f"{result.details['global_max']}"
    )

    print(
        f"expected: "
        f"{result.details['expected']}"
    )

    print(
        f"local_maxima: "
        f"{result.details['local_maxima']}"
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

    # ======================================================
    # M5 Communication Metrics
    # ======================================================

    print()

    print(
        "----- M5 Communication -----"
    )

    print(
        f"communication_messages: "
        f"{communication_messages}"
    )

    print(
        f"optimal_message_count: "
        f"{optimal_message_count}"
    )

    print(
        f"rounds: "
        f"{rounds}"
    )

    print(
        f"communication_redundancy_ratio: "
        f"{communication_redundancy_ratio:.4f}"
    )

    print(
        f"topological_fidelity: "
        f"{topological_fidelity:.4f}"
    )

    print(
        f"communication_trace: "
        f"{communication_trace}"
    )

    print()

    print(
        f"duration_seconds: "
        f"{result.duration_seconds:.4f}"
    )

    print("=" * 60)

    # ======================================================
    # Functional correctness
    # ======================================================

    assert result.success is True

    assert (
        result.details["global_max"]
        == 827
    )

    assert (
        result.details["expected"]
        == 827
    )

    assert (
        result.details["local_maxima"]
        == [827, 780]
    )

    # ======================================================
    # Real LLM assertions
    # ======================================================

    assert result.llm_calls == 2

    assert result.total_tokens > 0

    assert result.input_tokens > 0

    assert result.output_tokens > 0

    # ======================================================
    # Component execution assertions
    # ======================================================

    assert result.agent_count == 2

    assert result.component_calls == 3

    # ======================================================
    # M5 communication assertions
    # ======================================================

    # I-01 with 2 agents:
    #
    # Agent 1 → Agent 0
    # Agent 0 → Agent 1
    #
    # Total = 2 messages.
    assert (
        communication_messages
        == 2
    )

    assert (
        optimal_message_count
        == 2
    )

    # One collection round + one
    # broadcast round.
    assert rounds == 2

    # Empirical / optimal = 2 / 2.
    assert (
        communication_redundancy_ratio
        == 1.0
    )

    # Empirical topology exactly matches
    # the optimal topology.
    assert (
        topological_fidelity
        == 1.0
    )

    # ======================================================
    # Communication trace assertions
    # ======================================================

    assert (
        len(communication_trace)
        == 2
    )

    first_message = (
        communication_trace[0]
    )

    second_message = (
        communication_trace[1]
    )

    # ------------------------------------------------------
    # Round 1:
    #
    # Agent 1 → Agent 0
    # local_max
    # ------------------------------------------------------

    assert (
        first_message["sender"]
        == 1
    )

    assert (
        first_message["receiver"]
        == 0
    )

    assert (
        first_message["round"]
        == 1
    )

    assert (
        first_message["message_type"]
        == "local_max"
    )

    assert (
        first_message["payload"]
        == 780
    )

    # ------------------------------------------------------
    # Round 2:
    #
    # Agent 0 → Agent 1
    # global_max
    # ------------------------------------------------------

    assert (
        second_message["sender"]
        == 0
    )

    assert (
        second_message["receiver"]
        == 1
    )

    assert (
        second_message["round"]
        == 2
    )

    assert (
        second_message["message_type"]
        == "global_max"
    )

    assert (
        second_message["payload"]
        == 827
    )