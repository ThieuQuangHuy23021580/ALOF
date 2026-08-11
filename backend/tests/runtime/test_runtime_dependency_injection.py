from __future__ import annotations

from backend.application.runtime.runtime_context import (
    RuntimeContext,
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
            "title": "Python",
            "content": "Python is a programming language.",
            "summary": "Python basics."
        }
        """


def test_sequential_runtime_dependency_injection():

    ComponentRegistry.clear()

    ComponentRegistry.register(
        MentorComponent,
    )

    workflow = Workflow()

    workflow.add_node(
        WorkflowNode(
            id="step_1",
            component_id="mentor",
            objective="Explain Python",
            expected_output="Lesson",
        )
    )

    context = RuntimeContext(
        workflow=workflow,
    )

    llm = LLMService(
        provider=FakeLLMProvider(),
    )

    runtime = SequentialRuntime(
        dependencies={
            "llm": llm,
        },
    )

    result = runtime.run(
        context,
    )

    assert result.status.value == "completed"

    assert result.execution_order == [
        "step_1",
    ]

    assert result.final_artifact is not None

    assert result.final_artifact.content == (
        "Python is a programming language."
    )