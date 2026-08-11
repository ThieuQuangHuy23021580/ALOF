from __future__ import annotations

from backend.application.orchestration.execution_request import (
    ExecutionRequest,
)
from backend.application.orchestration.learning_orchestrator import (
    LearningOrchestrator,
)
from backend.application.planning.sequential_planner import (
    SequentialPlanner,
)
from backend.application.planning.sequential_workflow_builder import (
    SequentialWorkflowBuilder,
)
from backend.application.routing.router import Router
from backend.application.routing.routing_result import (
    RoutingResult,
)
from backend.application.runtime.sequential_runtime import (
    SequentialRuntime,
)
from backend.application.services.llm_service import (
    LLMService,
)

from backend.components.mentor.mentor_component import (
    MentorComponent,
)

from backend.core.component_registry import (
    ComponentRegistry,
)

from backend.domain.student.student import (
    Student,
)


class FakeRouter(Router):

    def route(
        self,
        student: Student,
        message: str,
    ) -> RoutingResult:

        return RoutingResult(
            intent="explain",
            candidate_components=[
                "mentor",
            ],
            confidence=1.0,
        )


class FakeLLMProvider:

    def generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:

        return """
        {
            "title": "Python Basics",
            "content": "Python is a high-level programming language.",
            "summary": "Introduction to Python."
        }
        """


def test_learning_orchestrator_dependency_injection():

    ComponentRegistry.clear()

    ComponentRegistry.register(
        MentorComponent,
    )

    llm = LLMService(
        provider=FakeLLMProvider(),
    )

    runtime = SequentialRuntime(
        dependencies={
            "llm": llm,
        },
    )

    orchestrator = LearningOrchestrator(
        router=FakeRouter(),
        planner=SequentialPlanner(),
        workflow_builder=SequentialWorkflowBuilder(),
        runtime=runtime,
    )

    request = ExecutionRequest(
        student=Student(
            display_name="Test Student",
        ),
        message="Explain Python",
    )

    result = orchestrator.execute(
        request,
    )

    assert result.status.value == "completed"

    assert result.execution_order == [
        "step_1",
    ]

    assert result.final_artifact is not None

    assert result.final_artifact.content == (
        "Python is a high-level programming language."
    )

    assert result.final_artifact.producer == "mentor"