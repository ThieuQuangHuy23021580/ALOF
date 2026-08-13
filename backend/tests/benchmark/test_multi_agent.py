from __future__ import annotations

from backend.application.services.llm_service import (
    LLMService,
)
from backend.benchmark.multi_agent import (
    MultiAgentBaseline,
)
from backend.benchmark.scenario import (
    BenchmarkScenario,
)
from backend.components.mentor.mentor_component import (
    MentorComponent,
)
from backend.components.research.research_component import (
    ResearchComponent,
)
from backend.core.component_registry import (
    ComponentRegistry,
)
from backend.domain.artifact.artifact_type import (
    ArtifactType,
)


class FakeLLMProvider:
    """
    Fake provider for multi-agent benchmark tests.
    """

    def __init__(self) -> None:

        self.responses = [
            """
            {
                "title": "Python Research",
                "content": "Python là ngôn ngữ lập trình cấp cao.",
                "summary": "Tổng quan về Python."
            }
            """,
            """
            {
                "title": "Python Lesson",
                "content": "Python là ngôn ngữ lập trình cấp cao và dễ đọc.",
                "summary": "Bài học giới thiệu Python."
            }
            """,
        ]

        self.calls = 0

    def generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:

        self.calls += 1

        assert self.responses

        return self.responses.pop(0)


def test_multi_agent_research_to_mentor():

    ComponentRegistry.clear()

    ComponentRegistry.register(
        ResearchComponent,
    )

    ComponentRegistry.register(
        MentorComponent,
    )

    provider = FakeLLMProvider()

    llm = LLMService(
        provider=provider,
    )

    scenario = BenchmarkScenario(
        id="research_to_mentor",
        name="Research to Mentor",
        user_request=(
            "Explain Python based on research."
        ),
        component_ids=[
            "research",
            "mentor",
        ],
        expected_output="Lesson",
    )

    baseline = MultiAgentBaseline(
        llm=llm,
    )

    result = baseline.run(
        scenario,
    )

    # ======================================================
    # Runtime
    # ======================================================

    assert (
        result.status.value
        == "completed"
    )

    # ======================================================
    # Execution
    # ======================================================

    assert result.execution_order == [
        "step_1",
        "step_2",
    ]

    # ======================================================
    # Artifacts
    # ======================================================

    assert (
        result.artifacts["step_1"].type
        == ArtifactType.RESEARCH
    )

    assert (
        result.artifacts["step_2"].type
        == ArtifactType.LESSON
    )

    # ======================================================
    # Final artifact
    # ======================================================

    assert (
        result.final_artifact
        is not None
    )

    assert (
        result.final_artifact.type
        == ArtifactType.LESSON
    )

    assert (
        result.final_artifact.producer
        == "mentor"
    )

    # ======================================================
    # LLM calls
    # ======================================================

    assert provider.calls == 2