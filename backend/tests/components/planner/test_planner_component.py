from __future__ import annotations

import pytest

from backend.application.runtime.runtime_context import (
    RuntimeContext,
)
from backend.application.services.llm_service import (
    LLMService,
)
from backend.components.planner.planner_component import (
    PlannerComponent,
)
from backend.core.component_context import (
    ComponentContext,
)
from backend.core.component_result import (
    ComponentResult,
)
from backend.core.dependency_context import (
    DependencyContext,
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
    Fake provider for testing PlannerComponent.
    """

    def generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:

        return """
        {
            "title": "Python Learning Plan",
            "content": "Learn Python basics, practice functions, and build a small project.",
            "summary": "A structured learning plan for Python."
        }
        """


class InvalidJSONProvider:
    """
    Fake provider that returns invalid JSON.
    """

    def generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:

        return "This is not valid JSON."


class InvalidSchemaProvider:
    """
    Fake provider that returns valid JSON
    with an invalid ArtifactPayload schema.
    """

    def generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:

        return """
        {
            "title": "Python Learning Plan"
        }
        """


def create_context(
    llm: LLMService | None = None,
) -> ComponentContext:

    workflow = Workflow()

    node = WorkflowNode(
        id="step_1",
        component_id="planner",
        objective="Create a learning plan for Python",
        expected_output="Learning Plan",
    )

    workflow.add_node(
        node,
    )

    runtime = RuntimeContext(
        workflow=workflow,
    )

    if llm is None:

        return ComponentContext(
            runtime=runtime,
            node=node,
        )

    return ComponentContext(
        runtime=runtime,
        node=node,
        dependencies=DependencyContext(
            dependencies={
                "llm": llm,
            },
        ),
    )


def test_planner_component_execution():

    llm = LLMService(
        provider=FakeLLMProvider(),
    )

    component = PlannerComponent()

    context = create_context(
        llm,
    )

    result = component.invoke(
        context,
    )

    assert isinstance(
        result,
        ComponentResult,
    )

    assert (
        result.artifact.type
        == ArtifactType.ROADMAP
    )

    assert (
        result.artifact.title
        == "Python Learning Plan"
    )

    assert (
        result.artifact.content
        == (
            "Learn Python basics, practice functions, "
            "and build a small project."
        )
    )

    assert (
        result.artifact.summary
        == "A structured learning plan for Python."
    )

    assert (
        result.artifact.producer
        == "planner"
    )


def test_planner_component_requires_llm_dependency():

    component = PlannerComponent()

    context = create_context()

    with pytest.raises(
        TypeError,
        match="LLMService",
    ):
        component.invoke(
            context,
        )


def test_planner_component_rejects_invalid_json():

    llm = LLMService(
        provider=InvalidJSONProvider(),
    )

    component = PlannerComponent()

    context = create_context(
        llm,
    )

    with pytest.raises(
        ValueError,
        match="Invalid JSON response",
    ):
        component.invoke(
            context,
        )


def test_planner_component_rejects_invalid_schema():

    llm = LLMService(
        provider=InvalidSchemaProvider(),
    )

    component = PlannerComponent()

    context = create_context(
        llm,
    )

    with pytest.raises(
        ValueError,
        match="Invalid response schema",
    ):
        component.invoke(
            context,
        )