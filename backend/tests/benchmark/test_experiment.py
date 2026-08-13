from __future__ import annotations

from backend.application.services.llm_service import (
    LLMService,
)
from backend.benchmark.experiment import (
    BenchmarkExperiment,
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


class FakeLLMProvider:
    """
    Fake provider for the first benchmark experiment.
    """

    def __init__(self) -> None:

        self.calls = 0

        self.responses = [
            # Single Agent
            "Python là ngôn ngữ lập trình cấp cao.",

            # Multi Agent - Research
            """
            {
                "title": "Python Research",
                "content": "Python là ngôn ngữ lập trình cấp cao.",
                "summary": "Tổng quan về Python."
            }
            """,

            # Multi Agent - Mentor
            """
            {
                "title": "Python Lesson",
                "content": "Python là ngôn ngữ lập trình cấp cao và dễ đọc.",
                "summary": "Bài học giới thiệu Python."
            }
            """,
        ]

    def generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:

        self.calls += 1

        assert self.responses

        return self.responses.pop(0)


def create_scenario() -> BenchmarkScenario:

    return BenchmarkScenario(
        id="python_explanation",
        name="Python Explanation",
        user_request="Explain Python.",
        component_ids=[
            "research",
            "mentor",
        ],
        expected_output="Lesson",
    )


def test_first_benchmark_experiment():

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

    experiment = BenchmarkExperiment(
        llm=llm,
    )

    scenario = create_scenario()

    single_result = (
        experiment.run_single_agent(
            scenario,
        )
    )

    assert (
        single_result.scenario_id
        == "python_explanation"
    )

    assert (
        single_result.approach
        == "single_agent"
    )

    assert single_result.success is True

    assert (
        single_result.output
        == "Python là ngôn ngữ lập trình cấp cao."
    )

    multi_result = (
        experiment.run_multi_agent(
            scenario,
        )
    )

    assert (
        multi_result.scenario_id
        == "python_explanation"
    )

    assert (
        multi_result.approach
        == "multi_agent"
    )

    assert multi_result.success is True

    assert (
        multi_result.output
        == "Python là ngôn ngữ lập trình cấp cao và dễ đọc."
    )

    assert (
        multi_result.metadata[
            "execution_order"
        ]
        == [
            "step_1",
            "step_2",
        ]
    )

    assert (
        single_result.metadata["duration"]
        >= 0
    )

    assert (
        multi_result.metadata["duration"]
        >= 0
    )