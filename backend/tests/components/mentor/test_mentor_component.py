from __future__ import annotations

from backend.application.runtime.runtime_context import (
    RuntimeContext,
)
from backend.application.services.llm_service import (
    LLMService,
)
from backend.components.mentor.mentor_component import (
    MentorComponent,
)
from backend.core.component_context import (
    ComponentContext,
)
from backend.core.component_result import (
    ComponentResult,
)
from backend.domain.artifact.artifact_type import (
    ArtifactType,
)
from backend.domain.workflow.workflow import (
    Workflow,
)
from backend.domain.workflow.workflow_node import (
    WorkflowNode,
)


class FakeLLMProvider:
    """
    Fake provider for testing MentorComponent.
    """

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


def test_mentor_component_execution():

    llm = LLMService(
        provider=FakeLLMProvider(),
    )

    component = MentorComponent(
        llm=llm,
    )

    # ======================================================
    # Runtime
    # ======================================================

    workflow = Workflow()

    node = WorkflowNode(
        id="step_1",
        component_id="mentor",
        objective="Explain Python",
        expected_output="Lesson",
    )

    workflow.add_node(
        node,
    )

    runtime = RuntimeContext(
        workflow=workflow,
    )

    # ======================================================
    # Component Context
    # ======================================================

    context = ComponentContext(
        runtime=runtime,
        node=node,
    )

    # ======================================================
    # Execute
    # ======================================================

    result = component.invoke(
        context,
    )

    # ======================================================
    # Assertions
    # ======================================================

    assert isinstance(
        result,
        ComponentResult,
    )

    assert (
        result.artifact.type
        == ArtifactType.LESSON
    )

    assert (
        result.artifact.title
        == "Python Basics"
    )

    assert (
        result.artifact.content
        == "Python is a high-level programming language."
    )

    assert (
        result.artifact.producer
        == "mentor"
    )