from __future__ import annotations

import pytest

from backend.application.runtime.runtime_context import (
    RuntimeContext,
)
from backend.application.services.llm_service import (
    LLMService,
)
from backend.components.research.research_component import (
    ResearchComponent,
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


# ==========================================================
# Fake LLM Provider
# ==========================================================

class FakeLLMProvider:
    """Fake provider for testing ResearchComponent."""

    def generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:

        return """
        {
            "title": "Python Research",
            "content": "Python is a high-level programming language used for general-purpose software development.",
            "summary": "Objective research summary about Python."
        }
        """


# ==========================================================
# Invalid JSON Provider
# ==========================================================

class InvalidJSONProvider:

    def generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:

        return "not valid json"


# ==========================================================
# Invalid Schema Provider
# ==========================================================

class InvalidSchemaProvider:

    def generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:

        return """
        {
            "title": "Python Research"
        }
        """


# ==========================================================
# Helpers
# ==========================================================

def create_research_context(
    llm: LLMService | None = None,
) -> ComponentContext:

    workflow = Workflow()

    node = WorkflowNode(
        id="step_1",
        component_id="research",
        objective="Research Python",
        expected_output="Research",
    )

    workflow.add_node(
        node,
    )

    runtime = RuntimeContext(
        workflow=workflow,
    )

    if llm is not None:

        return ComponentContext(
            runtime=runtime,
            node=node,
            dependencies=DependencyContext(
                dependencies={
                    "llm": llm,
                },
            ),
        )

    return ComponentContext(
        runtime=runtime,
        node=node,
    )


# ==========================================================
# Research Component Execution
# ==========================================================

def test_research_component_execution():

    llm = LLMService(
        provider=FakeLLMProvider(),
    )

    component = ResearchComponent()

    context = create_research_context(
        llm=llm,
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
        == ArtifactType.RESEARCH
    )

    assert (
        result.artifact.title
        == "Python Research"
    )

    assert (
        result.artifact.content
        == (
            "Python is a high-level programming "
            "language used for general-purpose "
            "software development."
        )
    )

    assert (
        result.artifact.summary
        == "Objective research summary about Python."
    )

    assert (
        result.artifact.producer
        == "research"
    )


# ==========================================================
# Dependency Injection
# ==========================================================

def test_research_component_requires_llm_dependency():

    component = ResearchComponent()

    context = create_research_context()

    with pytest.raises(
        TypeError,
        match="LLMService",
    ):
        component.invoke(
            context,
        )


def test_research_component_uses_llm_dependency_from_context():

    llm = LLMService(
        provider=FakeLLMProvider(),
    )

    component = ResearchComponent()

    context = create_research_context(
        llm=llm,
    )

    result = component.invoke(
        context,
    )

    assert result.artifact is not None

    assert (
        result.artifact.producer
        == "research"
    )

    assert (
        result.artifact.type
        == ArtifactType.RESEARCH
    )


# ==========================================================
# Invalid JSON
# ==========================================================

def test_research_component_rejects_invalid_json():

    llm = LLMService(
        provider=InvalidJSONProvider(),
    )

    component = ResearchComponent()

    context = create_research_context(
        llm=llm,
    )

    with pytest.raises(
        ValueError,
        match="Invalid JSON response",
    ):
        component.invoke(
            context,
        )


# ==========================================================
# Invalid Schema
# ==========================================================

def test_research_component_rejects_invalid_schema():

    llm = LLMService(
        provider=InvalidSchemaProvider(),
    )

    component = ResearchComponent()

    context = create_research_context(
        llm=llm,
    )

    with pytest.raises(
        ValueError,
        match="Invalid response schema",
    ):
        component.invoke(
            context,
        )