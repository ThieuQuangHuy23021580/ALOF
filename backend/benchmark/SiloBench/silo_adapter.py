from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.benchmark.SiloBench.scenario import (
    BenchmarkScenario,
)


class SILOBenchAdapter:
    """
    Converts a SILO-BENCH task JSON into an ALOF
    BenchmarkScenario.

    This class only performs data normalization.
    It does not execute the benchmark.
    """

    @staticmethod
    def load(
        task_file: str | Path,
    ) -> BenchmarkScenario:

        path = Path(task_file)

        if not path.exists():
            raise FileNotFoundError(
                f"SILO-BENCH task not found: {path}"
            )

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:

            data: dict[str, Any] = json.load(
                file,
            )

        agent_configs = data.get(
            "agent_configs",
            [],
        )

        agent_inputs: dict[int, Any] = {}

        for agent_config in agent_configs:

            agent_id = int(
                agent_config["agent_id"],
            )

            agent_inputs[agent_id] = (
                agent_config.get(
                    "input_shard",
                )
            )

        metadata = dict(
            data.get(
                "metadata",
                {},
            )
        )

        metadata["paradigm"] = data.get(
            "paradigm",
        )

        metadata["task_file"] = str(
            path.resolve(),
        )

        agent_count = len(
            agent_configs,
        )

        if agent_count == 0:

            configured_agent_count = (
                metadata.get(
                    "num_agents",
                )
            )

            if configured_agent_count is not None:

                agent_count = int(
                    configured_agent_count,
                )

        return BenchmarkScenario(
            id=data["case_id"],
            name=data["case_name"],
            user_request=data[
                "task_description"
            ],
            component_ids=[],
            expected_output=data[
                "expected_output"
            ],
            metadata=metadata,
            agent_count=agent_count,
            agent_inputs=agent_inputs,
        )