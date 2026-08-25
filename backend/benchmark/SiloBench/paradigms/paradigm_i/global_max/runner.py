from __future__ import annotations

import time

from backend.application.runtime.runtime_context import (
    RuntimeContext,
)
from backend.application.services.llm_service import (
    LLMService,
)
from backend.benchmark.SiloBench.communication import (
    CommunicationMetrics,
    CommunicationTrace,
)
from backend.benchmark.SiloBench.result import (
    BenchmarkResult,
)
from backend.benchmark.SiloBench.runner import (
    BenchmarkRunner,
)
from backend.benchmark.SiloBench.scenario import (
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


class ALOFBenchmarkRunner(
    BenchmarkRunner,
):
    """
    Executes benchmark scenarios using ALOF.

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

    # ======================================================
    # LLM
    # ======================================================

    @property
    def llm(
        self,
    ) -> LLMService:

        return self._llm

    # ======================================================
    # Benchmark execution
    # ======================================================

    def run(
        self,
        scenario: BenchmarkScenario,
    ) -> BenchmarkResult:

        started_at = time.perf_counter()

        # --------------------------------------------------
        # Reset LLM metrics from a previous benchmark run.
        # --------------------------------------------------

        self._llm.reset_call_count()

        # --------------------------------------------------
        # Communication trace.
        #
        # This is independent from the LLM metrics.
        # LLM calls != communication messages.
        # --------------------------------------------------

        communication_trace = (
            CommunicationTrace()
        )

        workflow = Workflow()

        runtime_context = RuntimeContext(
            workflow=workflow,
        )

        local_maxima: list[int] = []

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
                    "benchmark.global_max_llm"
                ),
                objective=scenario.user_request,
                expected_output=str(
                    scenario.expected_output,
                ),
            )

            workflow.add_node(
                node,
            )

            component = ComponentRegistry.create(
                "benchmark.global_max_llm",
            )

            # --------------------------------------------------
            # The same LLMService is shared across all agents.
            # --------------------------------------------------

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

            local_max = result.metadata.get(
                "local_max",
            )

            if not isinstance(
                local_max,
                int,
            ):
                raise TypeError(
                    "GlobalMaxLLMComponent must "
                    "return integer metadata "
                    "'local_max'."
                )

            local_maxima.append(
                local_max,
            )

            component_calls += 1

        # ==================================================
        # M5 — Communication: collect local maxima
        # ==================================================
        #
        # I-01 uses a Star/Tree aggregation topology.
        #
        # For n=2:
        #
        #   Agent 1 → Agent 0
        #
        # Agent 0 is the leader.
        #
        # Agent 0 already owns its own local_max, so only
        # Agent 1 needs to send its result to Agent 0.
        #
        # This is one logical communication message.
        # ==================================================

        leader_agent_id = 0

        for agent_id in range(
            scenario.agent_count,
        ):

            if agent_id == leader_agent_id:
                continue

            communication_trace.record(
                sender=agent_id,
                receiver=leader_agent_id,
                round=1,
                message_type="local_max",
                payload=local_maxima[
                    agent_id
                ],
            )

        # ==================================================
        # Deterministic global aggregation
        # ==================================================

        aggregator_node = WorkflowNode(
            id="global_aggregation",
            component_id=(
                "benchmark.global_max_aggregator"
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
            "benchmark.global_max_aggregator",
        )

        aggregator_context = ComponentContext(
            runtime=runtime_context,
            node=aggregator_node,
            inputs={
                "local_maxima": local_maxima,
            },
        )

        aggregation_result = aggregator.invoke(
            aggregator_context,
        )

        component_calls += 1

        global_max = aggregation_result.metadata.get(
            "global_max",
        )

        if not isinstance(
            global_max,
            int,
        ):
            raise TypeError(
                "GlobalMaxAggregatorComponent must "
                "return integer metadata "
                "'global_max'."
            )

        # ==================================================
        # M5 — Communication: broadcast global result
        # ==================================================
        #
        # Leader broadcasts the final result to every
        # non-leader agent.
        #
        # For n=2:
        #
        #   Agent 0 → Agent 1
        #
        # This is the second logical communication message.
        # ==================================================

        for agent_id in range(
            scenario.agent_count,
        ):

            if agent_id == leader_agent_id:
                continue

            communication_trace.record(
                sender=leader_agent_id,
                receiver=agent_id,
                round=2,
                message_type="global_max",
                payload=global_max,
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
            global_max == expected_value
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
        # M5 — Communication metrics
        # ==================================================
        #
        # I-01:
        #
        # Optimal topology:
        #
        #   Agent 1 → Agent 0
        #   Agent 0 → Agent 1
        #
        # Optimal messages = 2
        # ==================================================

        optimal_message_count = (
            2 * (scenario.agent_count - 1)
        )

        optimal_edges: set[
            tuple[int, int]
        ] = set()

        for agent_id in range(
            scenario.agent_count,
        ):

            if agent_id == leader_agent_id:
                continue

            optimal_edges.add(
                (
                    agent_id,
                    leader_agent_id,
                )
            )

            optimal_edges.add(
                (
                    leader_agent_id,
                    agent_id,
                )
            )

        communication_metrics = (
            CommunicationMetrics.build(
                trace=communication_trace,
                optimal_message_count=(
                    optimal_message_count
                ),
                optimal_edges=optimal_edges,
            )
        )

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
            rounds=communication_metrics[
                "rounds"
            ],
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
                communication_metrics[
                    "communication_messages"
                ]
            ),
            details={
                "global_max": global_max,
                "expected": expected_value,
                "local_maxima": local_maxima,

                # ------------------------------------------
                # LLM metrics
                # ------------------------------------------

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

                # ------------------------------------------
                # M5 communication metrics
                # ------------------------------------------

                "communication_redundancy_ratio": (
                    communication_metrics[
                        "communication_redundancy_ratio"
                    ]
                ),

                "topological_fidelity": (
                    communication_metrics[
                        "topological_fidelity"
                    ]
                ),

                "communication_trace": [
                    {
                        "sender": event.sender,
                        "receiver": event.receiver,
                        "round": event.round,
                        "message_type": (
                            event.message_type
                        ),
                        "payload": event.payload,
                    }
                    for event
                    in communication_trace.events
                ],

                "optimal_message_count": (
                    optimal_message_count
                ),

                "optimal_edges": [
                    list(edge)
                    for edge
                    in sorted(
                        optimal_edges
                    )
                ],
            },
        )