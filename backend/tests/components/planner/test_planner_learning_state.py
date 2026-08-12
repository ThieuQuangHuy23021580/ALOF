from __future__ import annotations

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
from backend.core.dependency_context import (
    DependencyContext,
)
from backend.domain.learning.learning_state import (
    LearningState,
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

        return """
        {
            "title": "Python Roadmap",
            "content": "Learn Python basics first.",
            "summary": "Basic Python roadmap."
        }
        """


def test_planner_can_access_learning_state():

    workflow = Workflow()

    node = WorkflowNode(
        id="planner",
        component_id="planner",
        objective="Create Python roadmap",
        expected_output="Roadmap",
    )

    workflow.add_node(
        node,
    )

    learning_state = LearningState(
        learner_id="learner-1",
        current_knowledge={
            "python": "basic",
        },
        progress={
            "python": 0.4,
        },
    )

    runtime = RuntimeContext(
        workflow=workflow,
        learning_state=learning_state,
    )

    context = ComponentContext(
        runtime=runtime,
        node=node,
        dependencies=DependencyContext(
            dependencies={
                "llm": LLMService(
                    provider=FakeLLMProvider(),
                ),
            },
        ),
    )

    assert (
        context.runtime.learning_state
        is learning_state
    )

    assert (
        context.runtime.learning_state.learner_id
        == "learner-1"
    )

    assert (
        context.runtime.learning_state.get_knowledge(
            "python",
        )
        == "basic"
    )

    assert (
        context.runtime.learning_state.get_progress(
            "python",
        )
        == 0.4
    )


def test_planner_component_execution_with_learning_state():

    workflow = Workflow()

    node = WorkflowNode(
        id="planner",
        component_id="planner",
        objective="Create Python roadmap",
        expected_output="Roadmap",
    )

    workflow.add_node(
        node,
    )

    runtime = RuntimeContext(
        workflow=workflow,
        learning_state=LearningState(
            learner_id="learner-1",
            current_knowledge={
                "python": "basic",
            },
            progress={
                "python": 0.4,
            },
        ),
    )

    context = ComponentContext(
        runtime=runtime,
        node=node,
        dependencies=DependencyContext(
            dependencies={
                "llm": LLMService(
                    provider=FakeLLMProvider(),
                ),
            },
        ),
    )

    component = PlannerComponent()

    result = component.invoke(
        context,
    )

    assert result.artifact is not None