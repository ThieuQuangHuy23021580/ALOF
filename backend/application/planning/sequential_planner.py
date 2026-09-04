from __future__ import annotations

from backend.application.routing.routing_result import (
    RoutingResult,
)

from .plan import Plan
from .planner import Planner
from .planning_request import PlanningRequest
from .plan_step import PlanStep


class SequentialPlanner(Planner):
    """
    Default sequential planner.

    Responsibilities
    ----------------
    - Convert RoutingResult into a logical execution plan.
    - Propagate adaptive teaching decisions into each relevant step.
    - Decide execution order.
    - Never build a Workflow.
    """

    def plan(
        self,
        request: PlanningRequest,
    ) -> Plan:

        routing = request.routing
        adaptive_learning = request.adaptive_learning
        teaching_action = adaptive_learning.teaching_action

        plan = Plan()

        previous_step: str | None = None

        for index, component in enumerate(
            routing.candidate_components,
            start=1,
        ):

            step = PlanStep(
                id=f"step_{index}",
                component=component,
                objective=self._objective(
                    component,
                    routing,
                ),
                expected_output=self._expected_output(
                    component,
                ),
            )

            # ==================================================
            # Adaptive teaching
            # ==================================================

            if self._should_apply_adaptive_teaching(
                component,
            ):
                step.set_adaptive_action(
                    action=teaching_action.action,
                    strategy=teaching_action.strategy,
                    difficulty=teaching_action.difficulty,
                    focus_concepts=teaching_action.focus_concepts,
                )

            # ==================================================
            # Dependencies
            # ==================================================

            if previous_step is not None:
                step.add_dependency(
                    previous_step,
                )

            previous_step = step.id

            plan.add_step(
                step,
            )

        return plan

    def _should_apply_adaptive_teaching(
        self,
        component: str,
    ) -> bool:
        """
        Determine whether adaptive teaching information
        should be attached to the execution step.
        """

        return component == "mentor"

    def _objective(
        self,
        component: str,
        routing: RoutingResult,
    ) -> str:

        match component:

            case "mentor":
                return (
                    "Explain and solve the current learner question "
                    "using the available execution context and evidence. "
                    "Adapt the explanation to the learner's diagnosed "
                    "knowledge level, weaknesses, misconceptions, and "
                    "teaching strategy. For comparison or reasoning tasks, "
                    "analyze the relevant concepts directly and provide "
                    "a clear, evidence-based explanation. Do not infer, "
                    "invent, or assume missing numerical values, diagram "
                    "details, answers, or visual information. If the "
                    "available evidence is insufficient to determine the "
                    "answer, explicitly state that the answer cannot be "
                    "determined from the provided evidence and explain "
                    "what information is missing."
                )

            case "planner":
                return (
                    "Create a structured learning roadmap."
                )

            case "quiz":
                return (
                    "Generate a quiz for the learner."
                )

            case "flashcard":
                return (
                    "Generate flashcards for revision."
                )

            case _:
                return (
                    f"Execute component '{component}'."
                )

    def _expected_output(
        self,
        component: str,
    ) -> str:

        match component:

            case "mentor":
                return "Lesson"

            case "planner":
                return "Learning Roadmap"

            case "quiz":
                return "Quiz"

            case "flashcard":
                return "Flashcards"

            case _:
                return "Artifact"