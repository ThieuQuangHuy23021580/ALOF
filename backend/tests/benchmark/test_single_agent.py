from __future__ import annotations

from backend.application.services.llm_service import (
    LLMService,
)
from backend.benchmark.scenario import (
    BenchmarkScenario,
)
from backend.benchmark.single_agent import (
    SingleAgentBaseline,
)


class FakeLLMProvider:
    """
    Fake provider for single-agent benchmark tests.
    """

    def __init__(self) -> None:

        self.calls = 0

    def generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:

        self.calls += 1

        assert len(messages) == 2

        assert (
            messages[0]["role"]
            == "system"
        )

        assert (
            messages[1]["role"]
            == "user"
        )

        return "Single-agent response."


def create_scenario() -> BenchmarkScenario:

    return BenchmarkScenario(
        id="single_mentor",
        name="Single Agent Mentor",
        user_request="Explain Python.",
        expected_output="lesson",
    )


def test_single_agent_baseline_execution():

    provider = FakeLLMProvider()

    llm = LLMService(
        provider=provider,
    )

    baseline = SingleAgentBaseline(
        llm=llm,
    )

    result = baseline.run(
        create_scenario(),
    )

    assert (
        result
        == "Single-agent response."
    )

    assert provider.calls == 1


def test_single_agent_uses_scenario_request():

    provider = FakeLLMProvider()

    llm = LLMService(
        provider=provider,
    )

    baseline = SingleAgentBaseline(
        llm=llm,
    )

    scenario = BenchmarkScenario(
        id="python",
        name="Python",
        user_request="Explain Python variables.",
        expected_output="lesson",
    )

    result = baseline.run(
        scenario,
    )

    assert (
        result
        == "Single-agent response."
    )

    assert provider.calls == 1