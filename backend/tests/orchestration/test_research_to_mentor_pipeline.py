from __future__ import annotations

from backend.application.runtime.runtime_context import (
    RuntimeContext,
)
from backend.components.mentor.mentor_component import (
    MentorComponent,
)
from backend.components.research.research_component import (
    ResearchComponent,
)
from backend.core.component_context import (
    ComponentContext,
)
from backend.core.dependency_context import (
    DependencyContext,
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
from backend.application.services.llm_service import (
    LLMService,
)


class FakeLLMProvider:

    def __init__(self):
        self.responses = [
            """
            {
                "title": "Python Research",
                "content": "Python là ngôn ngữ lập trình cấp cao, được sử dụng rộng rãi.",
                "summary": "Tổng quan về Python."
            }
            """,
            """
            {
                "title": "Python Lesson",
                "content": "Python là ngôn ngữ lập trình cấp cao, dễ đọc và phổ biến.",
                "summary": "Bài học giới thiệu Python."
            }
            """,
        ]

    def generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:

        return self.responses.pop(0)

def test_research_to_mentor_pipeline():

    llm = LLMService(
        provider=FakeLLMProvider(),
    )

    research = ResearchComponent()
    mentor = MentorComponent()

    workflow = Workflow()

    research_node = WorkflowNode(
        id="research",
        component_id="research",
        objective="Research Python",
        expected_output="Research",
    )

    mentor_node = WorkflowNode(
        id="mentor",
        component_id="mentor",
        objective="Explain Python based on research",
        expected_output="Lesson",
    )

    workflow.add_node(
        research_node,
    )

    workflow.add_node(
        mentor_node,
    )

    runtime = RuntimeContext(
        workflow=workflow,
    )

    # ======================================================
    # Research
    # ======================================================

    research_context = ComponentContext(
        runtime=runtime,
        node=research_node,
        dependencies=DependencyContext(
            dependencies={
                "llm": llm,
            },
        ),
    )

    research_result = research.invoke(
        research_context,
    )

    assert isinstance(
        research_result,
        ComponentResult,
    )

    assert (
        research_result.artifact.type
        == ArtifactType.RESEARCH
    )

    assert (
        research_result.artifact.content
        == "Python là ngôn ngữ lập trình cấp cao, được sử dụng rộng rãi."
    )

    runtime.add_artifact(
        "research",
        research_result.artifact,
    )

    # ======================================================
    # Mentor receives Research artifact
    # ======================================================

    mentor_context = ComponentContext(
        runtime=runtime,
        node=mentor_node,
        inputs={
            "research": research_result.artifact,
        },
        dependencies=DependencyContext(
            dependencies={
                "llm": llm,
            },
        ),
    )

    mentor_result = mentor.invoke(
        mentor_context,
    )

    # ======================================================
    # Assertions
    # ======================================================

    assert isinstance(
        mentor_result,
        ComponentResult,
    )

    assert (
        mentor_result.artifact.type
        == ArtifactType.LESSON
    )

    assert (
        mentor_result.artifact.producer
        == "mentor"
    )

    assert (
        mentor_result.artifact.title
        == "Python Lesson"
    )

    assert (
        mentor_result.artifact.content
        == "Python là ngôn ngữ lập trình cấp cao, dễ đọc và phổ biến."
    )