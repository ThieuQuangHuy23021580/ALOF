from __future__ import annotations

from backend.application.orchestration.execution_request import (
    ExecutionRequest,
)
from backend.application.orchestration.learning_orchestrator import (
    LearningOrchestrator,
)
from backend.application.planning.plan import Plan
from backend.application.planning.plan_step import PlanStep
from backend.application.planning.planner import Planner
from backend.application.planning.planning_request import PlanningRequest
from backend.application.planning.workflow_builder import WorkflowBuilder
from backend.application.routing.router import Router
from backend.application.routing.routing_result import RoutingResult
from backend.application.runtime.runtime import Runtime
from backend.application.runtime.runtime_context import RuntimeContext
from backend.application.services.llm_service import LLMService
from backend.components.mentor.mentor_component import MentorComponent
from backend.core.execution_status import ExecutionStatus
from backend.domain.learning.learning_state import LearningState
from backend.domain.student.student import Student
from backend.domain.workflow.workflow import Workflow
from backend.domain.workflow.workflow_node import WorkflowNode


class FakeRouter(Router):

    def route(
        self,
        student: Student,
        message: str,
    ) -> RoutingResult:

        return RoutingResult(
            intent="explain",
            confidence=0.95,
            candidate_components=[
                "mentor",
            ],
        )


class FakePlanner(Planner):

    def plan(
        self,
        request: PlanningRequest,
    ) -> Plan:

        assert (
            request.learning_state.learner_id
            == "learner-1"
        )

        assert (
            request.learning_state.current_knowledge[
                "rest"
            ]
            == "intermediate"
        )

        assert (
            request.learning_state.progress[
                "rest"
            ]
            == 0.7
        )

        return Plan(
            steps=[
                PlanStep(
                    id="step_1",
                    component="mentor",
                    objective=(
                        "Explain REST and GraphQL "
                        "for the learner."
                    ),
                    expected_output="Lesson",
                    depends_on=[],
                    metadata={},
                ),
            ],
            metadata={},
        )


class FakeWorkflowBuilder:

    def build(
        self,
        plan: Plan,
    ) -> Workflow:

        workflow = Workflow()

        for step in plan.steps:

            node = WorkflowNode(
                id=step.id,
                component_id=step.component,
                objective=step.objective,
                expected_output=step.expected_output,
                depends_on=step.depends_on,
                metadata=step.metadata,
            )

            workflow.add_node(
                node,
            )

        return workflow


class FakeLLMProvider:

    def __init__(self) -> None:
        self.messages: list[dict[str, str]] = []

        self.last_input_tokens = 0
        self.last_output_tokens = 0
        self.last_total_tokens = 0

    def generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:

        self.messages = messages

        response = """
        {
            "title": "REST and GraphQL Lesson",
            "content": "Lesson adapted to the learner's current knowledge.",
            "summary": "Adaptive lesson."
        }
        """.strip()

        self.last_input_tokens = sum(
            len(message["content"].split())
            for message in messages
        )

        self.last_output_tokens = len(
            response.split()
        )

        self.last_total_tokens = (
            self.last_input_tokens
            + self.last_output_tokens
        )

        return response


class FakeRuntime(Runtime):

    def __init__(
        self,
        provider: FakeLLMProvider,
    ) -> None:

        self.provider = provider
        self.received_context: RuntimeContext | None = None

        super().__init__()

    def run(
        self,
        context: RuntimeContext,
    ):
        self.received_context = context

        component = MentorComponent()

        from backend.core.component_context import (
            ComponentContext,
        )
        from backend.core.dependency_context import (
            DependencyContext,
        )

        component_context = ComponentContext(
            runtime=context,
            node=context.workflow.nodes[0],
            dependencies=DependencyContext(
                dependencies={
                    "llm": LLMService(
                        provider=self.provider,
                    ),
                },
            ),
        )

        result = component.invoke(
            component_context,
        )

        context.add_artifact(
            "step_1",
            result.artifact,
        )

        context.finish_execution()

        from backend.application.runtime.runtime_result import (
            RuntimeResult,
        )

        context.state = ExecutionStatus.COMPLETED

        return RuntimeResult(
            status=context.state,
            context=context,
        )


def test_adaptive_learning_end_to_end():

    # ==========================================================
    # Student
    # ==========================================================

    student = Student(
        id="learner-1",
        display_name="Adaptive Learner",
    )

    # ==========================================================
    # Learning State
    # ==========================================================

    learning_state = LearningState(
        learner_id="learner-1",
        current_knowledge={
            "rest": "intermediate",
            "graphql": "basic",
        },
        progress={
            "rest": 0.7,
            "graphql": 0.4,
        },
        metadata={
            "preferred_difficulty": "medium",
            "preferred_pace": "normal",
        },
    )

    request = ExecutionRequest(
        student=student,
        message=(
            "Giải thích REST và GraphQL "
            "cho tôi."
        ),
        learning_state=learning_state,
    )

    # ==========================================================
    # Dependencies
    # ==========================================================

    provider = FakeLLMProvider()

    runtime = FakeRuntime(
        provider=provider,
    )

    orchestrator = LearningOrchestrator(
        router=FakeRouter(),
        planner=FakePlanner(),
        workflow_builder=FakeWorkflowBuilder(),
        runtime=runtime,
    )

    # ==========================================================
    # Execute
    # ==========================================================

    result = orchestrator.execute(
        request,
    )

    # ==========================================================
    # Runtime
    # ==========================================================

    assert result is not None

    assert result.status == ExecutionStatus.COMPLETED

    assert runtime.received_context is not None

    context = runtime.received_context

    # ==========================================================
    # Learning State propagation
    # ==========================================================

    assert (
        context.learning_state
        is learning_state
    )

    assert (
        context.learning_state.learner_id
        == "learner-1"
    )

    assert (
        context.learning_state.current_knowledge[
            "rest"
        ]
        == "intermediate"
    )

    assert (
        context.learning_state.progress[
            "rest"
        ]
        == 0.7
    )

    assert (
        context.learning_state.metadata[
            "preferred_difficulty"
        ]
        == "medium"
    )

    # ==========================================================
    # Component output
    # ==========================================================

    artifact = context.get_artifact(
        "step_1",
    )

    assert artifact is not None

    # ==========================================================
    # LLM received adaptive context
    # ==========================================================

    assert provider.messages

    prompt = "\n".join(
        message["content"]
        for message in provider.messages
    )

    assert "learner-1" in prompt
    assert "intermediate" in prompt
    assert "basic" in prompt
    assert "0.7" in prompt
    assert "0.4" in prompt
    assert "medium" in prompt