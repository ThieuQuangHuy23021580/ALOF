from __future__ import annotations

from backend.application.runtime.runtime_context import (
    RuntimeContext,
)
from backend.application.runtime.sequential_runtime import (
    SequentialRuntime,
)
from backend.application.services.llm_service import (
    LLMService,
)
from backend.benchmark.scenario import (
    BenchmarkScenario,
)
from backend.core.component_registry import (
    ComponentRegistry,
)
from backend.domain.workflow.workflow import (
    Workflow,
)
from backend.domain.workflow.workflow_edge import (
    WorkflowEdge,
)
from backend.domain.workflow.workflow_node import (
    WorkflowNode,
)


class MultiAgentBaseline:
    """
    Executes a benchmark scenario through
    the existing ALOF multi-agent runtime.
    """

    def __init__(
        self,
        llm: LLMService,
    ) -> None:

        self._llm = llm

    def run(
        self,
        scenario: BenchmarkScenario,
    ):

        workflow = self._build_workflow(
            scenario,
        )

        runtime_context = RuntimeContext(
            workflow=workflow,
        )

        runtime = SequentialRuntime(
            dependencies={
                "llm": self._llm,
            },
        )

        return runtime.run(
            runtime_context,
        )

    def _build_workflow(
        self,
        scenario: BenchmarkScenario,
    ) -> Workflow:

        workflow = Workflow()

        component_ids = (
            scenario.component_ids
        )

        previous_node_id: str | None = None

        for index, component_id in enumerate(
            component_ids,
        ):

            node_id = (
                f"step_{index + 1}"
            )

            node = WorkflowNode(
                id=node_id,
                component_id=component_id,
                objective=scenario.user_request,
                expected_output=scenario.expected_output,
            )

            workflow.add_node(
                node,
            )

            if previous_node_id is not None:

                workflow.add_edge(
                    WorkflowEdge(
                        from_node=previous_node_id,
                        to_node=node_id,
                    ),
                )

            previous_node_id = node_id

        return workflow