from __future__ import annotations

from backend.application.planning.plan import Plan
from backend.application.planning.workflow_builder import (
    WorkflowBuilder,
)
from backend.domain.workflow.workflow import Workflow
from backend.domain.workflow.workflow_edge import WorkflowEdge
from backend.domain.workflow.workflow_node import WorkflowNode


class SequentialWorkflowBuilder(
    WorkflowBuilder,
):
    """
    Converts a logical execution Plan
    into an executable sequential Workflow.

    The builder preserves adaptive teaching
    information from PlanStep into WorkflowNode.
    """

    def build(
        self,
        plan: Plan,
    ) -> Workflow:

        workflow = Workflow()

        # ======================================================
        # Nodes
        # ======================================================

        for step in plan.steps:

            workflow.add_node(
                WorkflowNode(
                    id=step.id,
                    component_id=step.component,
                    objective=step.objective,
                    expected_output=step.expected_output,
                    depends_on=list(
                        step.depends_on,
                    ),

                    # ==========================================
                    # Adaptive teaching
                    # ==========================================

                    action=step.action,
                    strategy=step.strategy,
                    difficulty=step.difficulty,
                    focus_concepts=list(
                        step.focus_concepts,
                    ),

                    # ==========================================
                    # Metadata
                    # ==========================================

                    metadata=step.metadata.copy(),
                )
            )

        # ======================================================
        # Edges
        # ======================================================

        for step in plan.steps:

            for dependency in step.depends_on:

                workflow.add_edge(
                    WorkflowEdge(
                        from_node=dependency,
                        to_node=step.id,
                    )
                )

        return workflow