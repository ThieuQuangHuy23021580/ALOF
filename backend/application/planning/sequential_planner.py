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
    - Decide execution order.
    - Never build a Workflow.
    """

    def plan(
        self,
        request: PlanningRequest,
    ) -> Plan:

        routing = request.routing

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

            if previous_step is not None:

                step.add_dependency(
                    previous_step,
                )

            previous_step = step.id

            plan.add_step(
                step,
            )

        return plan

    def _objective(
        self,
        component: str,
        routing: RoutingResult,
    ) -> str:

        match component:

            case "mentor":
                return (
                    "Explain the requested topic clearly."
                )

            case "research":
                return (
                    "Analyze and organize the requested topic."
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

            case "research":
                return "Research Summary"

            case "planner":
                return "Learning Roadmap"

            case "quiz":
                return "Quiz"

            case "flashcard":
                return "Flashcards"

            case _:
                return "Artifact"