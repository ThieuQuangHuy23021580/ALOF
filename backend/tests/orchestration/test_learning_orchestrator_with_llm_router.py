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

from backend.application.routing.llm_router import (
    LLMRouter,
)

from backend.application.routing.intent_recognizer import (
    IntentRecognizer,
)

from backend.application.routing.intent_result import (
    IntentResult,
)

from backend.application.runtime.sequential_runtime import (
    SequentialRuntime,
)

from backend.core.component import Component
from backend.core.component_registry import (
    ComponentRegistry,
)

from backend.core.component_result import (
    ComponentResult,
)

from backend.domain.artifact.artifact import Artifact
from backend.domain.artifact.artifact_type import ArtifactType
from backend.domain.student.student import Student


class FakeIntentRecognizer(
    IntentRecognizer,
):

    def recognize(
        self,
        message: str,
    ) -> IntentResult:

        return IntentResult(
            intent="explain",
            confidence=1.0,
        )


class FakeComponent(Component):

    component_id = "mentor"

    name = "Fake"

    description = "Fake"


    def execute(
        self,
        context,
    ) -> ComponentResult:

        return ComponentResult(
            artifact=Artifact(
                type=ArtifactType.RESPONSE,
                title="Result",
                content="LLM Router Flow",
                producer=self.component_id,
            )
        )


def test_learning_orchestrator_with_llm_router():

    ComponentRegistry.clear()

    ComponentRegistry.register(
        FakeComponent,
    )


    router = LLMRouter(
        recognizer=FakeIntentRecognizer(),
    )


    orchestrator = LearningOrchestrator(
        router=router,
        planner=SequentialPlanner(),
        workflow_builder=SequentialWorkflowBuilder(),
        runtime=SequentialRuntime(),
    )


    request = ExecutionRequest(
        student=Student(
            display_name="Test",
        ),
        message="Explain Python",
    )


    result = orchestrator.execute(
        request,
    )


    assert result.status.value == "completed"

    assert result.final_artifact.content == (
        "LLM Router Flow"
    )