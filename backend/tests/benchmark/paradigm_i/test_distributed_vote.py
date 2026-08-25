from __future__ import annotations

import os
from pathlib import Path

from benchmark.SiloBench.paradigms.paradigm_i.distributed_vote.runner import (
    DistributedVoteBenchmarkRunner,
)
from benchmark.SiloBench.silo_adapter import (
    SILOBenchAdapter,
)
from backend.core.component_bootstrap import (
    register_components,
)


def test_alof_silo_distributed_vote_with_real_llm():

    register_components()

    silo_root = os.environ[
        "SILO_BENCH_ROOT"
    ]

    task_file = (
        Path(silo_root)
        / "benchmarks"
        / "I-03_n2.json"
    )

    scenario = SILOBenchAdapter.load(
        task_file,
    )

    runner = DistributedVoteBenchmarkRunner()

    result = runner.run(
        scenario,
    )

    print()
    print("=" * 60)
    print("ALOF × SILO-BENCH × REAL LLM")
    print("=" * 60)

    print(
        f"scenario_id: {result.scenario_id}"
    )
    print(
        f"scenario_name: {result.scenario_name}"
    )
    print(
        f"success: {result.success}"
    )
    print(
        f"winner: {result.details['winner']}"
    )
    print(
        f"expected: {result.details['expected']}"
    )
    print(
        f"local_vote_counts: "
        f"{result.details['local_vote_counts']}"
    )
    print(
        f"global_vote_counts: "
        f"{result.details['global_vote_counts']}"
    )
    print(
        f"agent_count: {result.agent_count}"
    )
    print(
        f"component_calls: "
        f"{result.component_calls}"
    )
    print(
        f"llm_calls: {result.llm_calls}"
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
    print("----- M5.5 Communication -----")

    print(
        f"communication_messages: "
        f"{result.details['communication_messages']}"
    )
    print(
        f"optimal_message_count: "
        f"{result.details['optimal_message_count']}"
    )
    print(
        f"rounds: "
        f"{result.details['rounds']}"
    )
    print(
        f"communication_redundancy_ratio: "
        f"{result.details['communication_redundancy_ratio']:.4f}"
    )
    print(
        f"topological_fidelity: "
        f"{result.details['topological_fidelity']:.4f}"
    )
    print(
        f"communication_trace: "
        f"{result.details['communication_trace']}"
    )

    print(
        f"duration_seconds: "
        f"{result.duration_seconds:.4f}"
    )

    print("=" * 60)

    assert result.llm_calls == 2

    assert result.total_tokens > 0

    assert result.details["winner"] == (
        "Candidate_D"
    )

    assert result.details[
        "global_vote_counts"
    ] == {
        "Candidate_D": 31,
        "Candidate_B": 6,
        "Candidate_A": 7,
        "Candidate_C": 6,
    }

    assert (
        result.details["communication_messages"]
        == 2
    )

    assert (
        result.details[
            "optimal_message_count"
        ]
        == 2
    )

    assert (
        result.details[
            "communication_redundancy_ratio"
        ]
        == 1.0
    )

    assert (
        result.details[
            "topological_fidelity"
        ]
        == 1.0
    )

    assert result.success is True