from __future__ import annotations

import os
import time
from pathlib import Path

from backend.application.runtime.runtime_context import (
    RuntimeContext,
)
from backend.application.services.llm_service import (
    LLMService,
)
from backend.benchmark.result import (
    BenchmarkResult,
)
from backend.benchmark.runner import (
    BenchmarkRunner,
)
from backend.benchmark.silo_adapter import (
    SILOBenchAdapter,
)
from backend.benchmark.scenario import (
    BenchmarkScenario,
)
from backend.benchmark.communication.bus import (
    BenchmarkCommunicationBus,
)
from backend.benchmark.communication.message import (
    BenchmarkMessage,
)
from backend.core.component_context import (
    ComponentContext,
)
from backend.core.component_registry import (
    ComponentRegistry,
)
from backend.core.dependency_context import (
    DependencyContext,
)
from backend.domain.workflow.workflow import (
    Workflow,
)
from backend.domain.workflow.workflow_node import (
    WorkflowNode,
)


class DistributedVoteBenchmarkRunner(
    BenchmarkRunner,
):
    """
    Executes SILO-BENCH I-03 using ALOF.

    Agent-local computation:
        private shard
            ↓
        LLM
            ↓
        local vote histogram

    Coordination:
        Agent 1 → Agent 0
        local histogram

        Agent 0 → Agent 1
        global winner

    Aggregation itself is deterministic.
    """

    def __init__(
        self,
        llm: LLMService | None = None,
    ) -> None:

        self._llm = (
            llm
            if llm is not None
            else LLMService()
        )

        self._communication_bus = (
            BenchmarkCommunicationBus()
        )

    @property
    def llm(
        self,
    ) -> LLMService:

        return self._llm

    @property
    def communication_bus(
        self,
    ) -> BenchmarkCommunicationBus:

        return self._communication_bus

    def run(
        self,
        scenario: BenchmarkScenario,
    ) -> BenchmarkResult:

        started_at = time.perf_counter()

        self._llm.reset_call_count()
        self._communication_bus.clear()

        workflow = Workflow()

        runtime_context = RuntimeContext(
            workflow=workflow,
        )

        local_vote_counts: list[dict[str, int]] = []

        component_calls = 0

        # ==================================================
        # Agent-local LLM execution
        # ==================================================

        for agent_id in range(
            scenario.agent_count,
        ):

            node = WorkflowNode(
                id=f"agent_{agent_id}",
                component_id=(
                    "benchmark.distributed_vote_llm"
                ),
                objective=scenario.user_request,
                expected_output=str(
                    scenario.expected_output,
                ),
            )

            workflow.add_node(node)

            component = ComponentRegistry.create(
                "benchmark.distributed_vote_llm",
            )

            component_context = ComponentContext(
                runtime=runtime_context,
                node=node,
                inputs={
                    "agent_id": agent_id,
                    "input_shard": (
                        scenario.agent_inputs[
                            agent_id
                        ]
                    ),
                },
                dependencies=DependencyContext(
                    dependencies={
                        "llm": self._llm,
                    },
                ),
            )

            result = component.invoke(
                component_context,
            )

            counts = result.metadata.get(
                "local_vote_counts",
            )

            if not isinstance(counts, dict):
                raise TypeError(
                    "DistributedVoteLLMComponent must "
                    "return dict metadata "
                    "'local_vote_counts'."
                )

            local_vote_counts.append(
                counts,
            )

            component_calls += 1

        # ==================================================
        # Communication: Agent 1 → Agent 0
        # ==================================================

        if scenario.agent_count >= 2:

            self._communication_bus.send(
                BenchmarkMessage(
                    sender_id=1,
                    receiver_id=0,
                    round=1,
                    message_type="local_vote_counts",
                    payload={
                        "local_vote_counts": (
                            local_vote_counts[1]
                        ),
                    },
                ),
            )

        # ==================================================
        # Deterministic aggregation
        # ==================================================

        aggregator_node = WorkflowNode(
            id="global_aggregation",
            component_id=(
                "benchmark.distributed_vote_aggregator"
            ),
            objective=scenario.user_request,
            expected_output=str(
                scenario.expected_output,
            ),
        )

        workflow.add_node(
            aggregator_node,
        )

        aggregator = ComponentRegistry.create(
            "benchmark.distributed_vote_aggregator",
        )

        aggregator_context = ComponentContext(
            runtime=runtime_context,
            node=aggregator_node,
            inputs={
                "local_vote_counts": (
                    local_vote_counts
                ),
            },
        )

        aggregation_result = aggregator.invoke(
            aggregator_context,
        )

        component_calls += 1

        global_vote_counts = (
            aggregation_result.metadata.get(
                "global_vote_counts",
            )
        )

        winner = aggregation_result.metadata.get(
            "winner",
        )

        if not isinstance(
            global_vote_counts,
            dict,
        ):
            raise TypeError(
                "DistributedVoteAggregatorComponent "
                "must return dict metadata "
                "'global_vote_counts'."
            )

        if not isinstance(
            winner,
            str,
        ):
            raise TypeError(
                "DistributedVoteAggregatorComponent "
                "must return string metadata "
                "'winner'."
            )

        # ==================================================
        # Communication: Agent 0 → Agent 1
        # ==================================================

        if scenario.agent_count >= 2:

            self._communication_bus.send(
                BenchmarkMessage(
                    sender_id=0,
                    receiver_id=1,
                    round=2,
                    message_type="global_winner",
                    payload={
                        "winner": winner,
                    },
                ),
            )

        # ==================================================
        # Evaluation
        # ==================================================

        expected = scenario.expected_output

        expected_values = expected[
            "per_agent_values"
        ]

        expected_value = expected_values[0]

        success = (
            winner == expected_value
            and all(
                value == expected_value
                for value in expected_values
            )
        )

        duration = (
            time.perf_counter()
            - started_at
        )

        communication_messages = (
            self._communication_bus.messages
        )

        optimal_message_count = 2

        communication_redundancy_ratio = (
            len(communication_messages)
            / optimal_message_count
        )

        topological_fidelity = (
            1.0
            if len(communication_messages)
            == optimal_message_count
            else 0.0
        )

        return BenchmarkResult(
            scenario_id=scenario.id,
            scenario_name=scenario.name,
            success=success,
            agent_count=scenario.agent_count,
            duration_seconds=duration,
            component_calls=component_calls,
            llm_calls=self._llm.call_count,
            input_tokens=(
                self._llm.total_input_tokens
            ),
            output_tokens=(
                self._llm.total_output_tokens
            ),
            total_tokens=(
                self._llm.total_tokens
            ),
            details={
                "winner": winner,
                "expected": expected_value,
                "local_vote_counts": (
                    local_vote_counts
                ),
                "global_vote_counts": (
                    global_vote_counts
                ),
                "communication_messages": (
                    len(communication_messages)
                ),
                "optimal_message_count": (
                    optimal_message_count
                ),
                "rounds": (
                    max(
                        (
                            message.round
                            for message
                            in communication_messages
                        ),
                        default=0,
                    )
                ),
                "communication_redundancy_ratio": (
                    communication_redundancy_ratio
                ),
                "topological_fidelity": (
                    topological_fidelity
                ),
                "communication_trace": [
                    {
                        "sender": message.sender_id,
                        "receiver": message.receiver_id,
                        "round": message.round,
                        "message_type": (
                            message.message_type
                        ),
                        "payload": message.payload,
                    }
                    for message
                    in communication_messages
                ],
                "llm_metrics": [
                    {
                        "stage": metric.stage,
                        "component": metric.component,
                        "duration": metric.duration,
                        "input_tokens": (
                            metric.input_tokens
                        ),
                        "output_tokens": (
                            metric.output_tokens
                        ),
                        "total_tokens": (
                            metric.total_tokens
                        ),
                    }
                    for metric
                    in self._llm.call_metrics
                ],
            },
        )