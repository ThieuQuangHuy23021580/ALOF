
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
from backend.core.component_registry import (
    ComponentRegistry,
)
from backend.core.dependency_context import (
    DependencyContext,
)
from backend.domain.workflow.workflow import (
    Workflow,
)
from backend.domain.workflow.workflow_node import (
    WorkflowNode,
)


class FakeLLMProvider:

    def generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:

        return "fake"


def create_runtime_context() -> RuntimeContext:

    workflow = Workflow(
        nodes=[
            WorkflowNode(
                id="step_1",
                component_id="mentor",
                objective="Explain Python",
            ),
        ],
    )

    return RuntimeContext(
        workflow=workflow,
    )


def test_component_registry_creates_component_without_dependencies():

    ComponentRegistry.clear()

    ComponentRegistry.register(
        MentorComponent,
    )

    component = ComponentRegistry.create(
        "mentor",
    )

    assert isinstance(
        component,
        MentorComponent,
    )


def test_component_context_provides_runtime_dependency():

    ComponentRegistry.clear()

    ComponentRegistry.register(
        MentorComponent,
    )

    llm = LLMService(
        provider=FakeLLMProvider(),
    )

    component = ComponentRegistry.create(
        "mentor",
    )

    runtime = create_runtime_context()

    node = runtime.workflow.get_node(
        "step_1",
    )

    assert node is not None

    context = ComponentContext(
        runtime=runtime,
        node=node,
        dependencies=DependencyContext(
            dependencies={
                "llm": llm,
            },
        ),
    )

    resolved_llm = context.get_dependency(
        "llm",
    )

    assert resolved_llm is llm

    assert context.has_dependency(
        "llm",
    )


def test_mentor_component_uses_dependency_from_context():

    ComponentRegistry.clear()

    ComponentRegistry.register(
        MentorComponent,
    )

    llm = LLMService(
        provider=FakeLLMProvider(),
    )

    component = ComponentRegistry.create(
        "mentor",
    )

    runtime = create_runtime_context()

    node = runtime.workflow.get_node(
        "step_1",
    )

    assert node is not None

    context = ComponentContext(
        runtime=runtime,
        node=node,
        dependencies=DependencyContext(
            dependencies={
                "llm": llm,
            },
        ),
    )

    resolved_llm = context.get_dependency(
        "llm",
    )

    assert resolved_llm is llm

    assert not hasattr(
        component,
        "_llm",
    )

