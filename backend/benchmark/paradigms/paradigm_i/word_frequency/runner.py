from __future__ import annotations

import time

from backend.application.runtime.runtime_context import (
    RuntimeContext,
)
from backend.application.services.llm_service import (
    LLMService,
)
from backend.benchmark.communication.bus import (
    BenchmarkCommunicationBus,
)
from backend.benchmark.communication.message import (
    BenchmarkMessage,
)
from backend.benchmark.result import (
    BenchmarkResult,
)
from backend.benchmark.runner import (
    BenchmarkRunner,
)
from backend.benchmark.scenario import (
    BenchmarkScenario,
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


class WordFrequencyBenchmarkRunner(
    BenchmarkRunner,
):
    """
    Executes SILO-BENCH I-02: Word Frequency.

    Two-agent protocol:

        Agent 1 -> Agent 0
            local_count

        Agent 0 -> Agent 1
            global_count

    The LLM performs only agent-local computation.
    Coordination is explicitly represented through
    BenchmarkCommunicationBus.
    """

    COMPONENT_ID = (
        "benchmark.word_frequency_llm"
    )

    AGGREGATOR_COMPONENT_ID = (
        "benchmark.word_frequency_aggregator"
    )

    TARGET_WORD = "apple"

    def __init__(
        self,
        llm: LLMService | None = None,
    ) -> None:

        self._llm = (
            llm
            if llm is not None
            else LLMService()
        )

    @property
    def llm(
        self,
    ) -> LLMService:

        return self._llm

    def run(
        self,
        scenario: BenchmarkScenario,
    ) -> BenchmarkResult:

        started_at = time.perf_counter()

        self._llm.reset_call_count()

        workflow = Workflow()

        runtime_context = RuntimeContext(
            workflow=workflow,
        )

        bus = BenchmarkCommunicationBus()

        local_counts: list[int] = []

        component_calls = 0

        # ==================================================
        # Phase 1 — Agent-local LLM computation
        # ==================================================

        for agent_id in range(
            scenario.agent_count,
        ):

            node = WorkflowNode(
                id=f"agent_{agent_id}",
                component_id=self.COMPONENT_ID,
                objective=scenario.user_request,
                expected_output=str(
                    scenario.expected_output,
                ),
            )

            workflow.add_node(
                node,
            )

            component = ComponentRegistry.create(
                self.COMPONENT_ID,
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
                    "target_word": self.TARGET_WORD,
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

            local_count = result.metadata.get(
                "local_count",
            )

            if not isinstance(
                local_count,
                int,
            ):
                raise TypeError(
                    "WordFrequencyLLMComponent must "
                    "return integer metadata "
                    "'local_count'."
                )

            local_counts.append(
                local_count,
            )

            component_calls += 1

        # ==================================================
        # Phase 2 — P2P collection
        #
        # Agent 1 sends its local count to Agent 0.
        # ==================================================

        bus.send(
            BenchmarkMessage(
                sender_id=1,
                receiver_id=0,
                round=1,
                message_type="local_count",
                payload={
                    "target_word": self.TARGET_WORD,
                    "value": local_counts[1],
                },
            )
        )

        received_by_agent_0 = bus.messages_for(
            receiver_id=0,
        )

        remote_counts = [
            message.payload["value"]
            for message in received_by_agent_0
            if message.message_type
            == "local_count"
        ]

        if len(remote_counts) != 1:
            raise RuntimeError(
                "Agent 0 must receive exactly "
                "one local_count message."
            )

        # ==================================================
        # Phase 3 — Global aggregation at Agent 0
        # ==================================================

        aggregator_node = WorkflowNode(
            id="global_aggregation",
            component_id=(
                self.AGGREGATOR_COMPONENT_ID
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
            self.AGGREGATOR_COMPONENT_ID,
        )

        aggregation_inputs = [
            local_counts[0],
            *remote_counts,
        ]

        aggregator_context = ComponentContext(
            runtime=runtime_context,
            node=aggregator_node,
            inputs={
                "local_counts": aggregation_inputs,
            },
        )

        aggregation_result = aggregator.invoke(
            aggregator_context,
        )

        component_calls += 1

        total_count = aggregation_result.metadata.get(
            "total_count",
        )

        if not isinstance(
            total_count,
            int,
        ):
            raise TypeError(
                "WordFrequencyAggregatorComponent "
                "must return integer metadata "
                "'total_count'."
            )

        # ==================================================
        # Phase 4 — Broadcast global result
        #
        # Agent 0 sends the final result to Agent 1.
        # ==================================================

        bus.send(
            BenchmarkMessage(
                sender_id=0,
                receiver_id=1,
                round=2,
                message_type="global_count",
                payload={
                    "target_word": self.TARGET_WORD,
                    "value": total_count,
                },
            )
        )

        received_by_agent_1 = bus.messages_for(
            receiver_id=1,
        )

        global_messages = [
            message
            for message in received_by_agent_1
            if message.message_type
            == "global_count"
        ]

        if len(global_messages) != 1:
            raise RuntimeError(
                "Agent 1 must receive exactly "
                "one global_count message."
            )

        received_global_count = (
            global_messages[0]
            .payload["value"]
        )

        if (
            received_global_count
            != total_count
        ):
            raise RuntimeError(
                "Broadcast global_count does not "
                "match aggregated total_count."
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
            total_count == expected_value
            and all(
                value == expected_value
                for value in expected_values
            )
        )

        duration = (
            time.perf_counter()
            - started_at
        )

        # ==================================================
        # Communication metrics
        # ==================================================

        communication_messages = (
            bus.message_count
        )

        optimal_message_count = 2

        rounds = max(
            (
                message.round
                for message in bus.messages
            ),
            default=0,
        )

        communication_redundancy_ratio = (
            communication_messages
            / optimal_message_count
        )

        empirical_edges = {
            (
                message.sender_id,
                message.receiver_id,
            )
            for message in bus.messages
        }

        optimal_edges = {
            (1, 0),
            (0, 1),
        }

        union = (
            empirical_edges
            | optimal_edges
        )

        intersection = (
            empirical_edges
            & optimal_edges
        )

        topological_fidelity = (
            len(intersection)
            / len(union)
            if union
            else 1.0
        )

        communication_trace = [
            {
                "sender": message.sender_id,
                "receiver": message.receiver_id,
                "round": message.round,
                "message_type": message.message_type,
                "payload": message.payload["value"],
            }
            for message in bus.messages
        ]

        # ==================================================
        # Result
        # ==================================================

        return BenchmarkResult(
            scenario_id=scenario.id,
            scenario_name=scenario.name,
            success=success,
            agent_count=scenario.agent_count,
            duration_seconds=duration,
            component_calls=component_calls,
            rounds=rounds,
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
            communication_messages=(
                communication_messages
            ),
            metrics={
                "communication_redundancy_ratio": (
                    communication_redundancy_ratio
                ),
                "topological_fidelity": (
                    topological_fidelity
                ),
            },
            details={
                "total_count": total_count,
                "expected": expected_value,
                "local_counts": local_counts,
                "target_word": self.TARGET_WORD,
                "optimal_message_count": (
                    optimal_message_count
                ),
                "communication_trace": (
                    communication_trace
                ),
                "llm_metrics": [
                    {
                        "stage": metric.stage,
                        "component": metric.component,
                        "duration": metric.duration,
                        "input_tokens": metric.input_tokens,
                        "output_tokens": metric.output_tokens,
                        "total_tokens": metric.total_tokens,
                    }
                    for metric in self._llm.call_metrics
                ],
            },
        )