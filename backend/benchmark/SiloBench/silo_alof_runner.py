from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.benchmark.SiloBench.scenario import BenchmarkScenario


@dataclass
class AgentExecution:
    agent_id: int
    input_data: list[int]
    local_result: int | None = None


@dataclass
class SiloALOFResult:
    case_id: str
    success: bool

    agent_outputs: dict[int, Any]

    rounds: int

    communication_count: int

    token_consumption: int

    metadata: dict[str, Any]


class SILOALOFRunner:
    """
    Executes SILO-BENCH scenarios using ALOF's
    multi-agent benchmark execution layer.

    This runner is intentionally separate from
    ALOF's production SequentialRuntime.

    The goal is to benchmark coordination behavior
    without modifying the ALOF core runtime.
    """

    def run(
        self,
        scenario: BenchmarkScenario,
    ) -> SiloALOFResult:

        agents = self._create_agents(
            scenario,
        )

        # ==================================================
        # Round 1
        #
        # Every agent computes its local result.
        # ==================================================

        for agent in agents:

            agent.local_result = max(
                agent.input_data,
            )

        # ==================================================
        # Communication
        #
        # Each agent sends local result to coordinator.
        # ==================================================

        communication_count = len(
            agents,
        )

        local_results = {
            agent.agent_id: agent.local_result
            for agent in agents
        }

        # ==================================================
        # Coordinator
        # ==================================================

        global_result = max(
            value
            for value in local_results.values()
            if value is not None
        )

        # ==================================================
        # Round 2
        #
        # Coordinator broadcasts global result.
        # ==================================================

        communication_count += len(
            agents,
        )

        agent_outputs = {
            agent.agent_id: global_result
            for agent in agents
        }

        # ==================================================
        # Evaluation
        # ==================================================

        expected = (
            scenario.expected_output
            .get(
                "per_agent_values",
                [],
            )
            if isinstance(
                scenario.expected_output,
                dict,
            )
            else []
        )

        expected_outputs = {
            index: value
            for index, value in enumerate(
                expected,
            )
        }

        success = (
            agent_outputs
            == expected_outputs
        )

        return SiloALOFResult(
            case_id=scenario.id,
            success=success,
            agent_outputs=agent_outputs,
            rounds=2,
            communication_count=communication_count,
            token_consumption=0,
            metadata={
                "agent_count": scenario.agent_count,
                "local_results": local_results,
                "expected_outputs": expected_outputs,
            },
        )

    def _create_agents(
        self,
        scenario: BenchmarkScenario,
    ) -> list[AgentExecution]:

        return [
            AgentExecution(
                agent_id=agent_id,
                input_data=list(
                    scenario.agent_inputs[
                        agent_id
                    ],
                ),
            )
            for agent_id in range(
                scenario.agent_count,
            )
        ]