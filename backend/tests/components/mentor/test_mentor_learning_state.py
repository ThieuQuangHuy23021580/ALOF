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
            "content": "REST is an architectural style for APIs. Since the learner already has intermediate REST knowledge and basic GraphQL knowledge, the lesson focuses on comparing REST with GraphQL.",
            "summary": "A learner-adapted comparison of REST and GraphQL."
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

def test_mentor_receives_learning_state():

    workflow = Workflow()

    node = WorkflowNode(
        id="mentor",
        component_id="mentor",
        objective=(
            "Explain REST and GraphQL "
            "for the learner."
        ),
        expected_output="Lesson",
    )

    workflow.add_node(
        node,
    )

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

    runtime = RuntimeContext(
        workflow=workflow,
        learning_state=learning_state,
    )

    provider = FakeLLMProvider()

    context = ComponentContext(
        runtime=runtime,
        node=node,
        dependencies=DependencyContext(
            dependencies={
                "llm": LLMService(
                    provider=provider,
                ),
            },
        ),
    )

    component = MentorComponent()

    result = component.invoke(
        context,
    )

    assert result.artifact is not None

    assert provider.messages

    prompt = "\n".join(
        message["content"]
        for message in provider.messages
    )

    assert "learner-1" in prompt

    assert "rest" in prompt

    assert "intermediate" in prompt

    assert "graphql" in prompt

    assert "basic" in prompt

    assert "0.7" in prompt

    assert "0.4" in prompt

    assert "medium" in prompt