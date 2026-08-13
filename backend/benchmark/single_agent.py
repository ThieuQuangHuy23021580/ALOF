from __future__ import annotations

from backend.application.services.llm_service import (
    LLMService,
)
from backend.benchmark.scenario import (
    BenchmarkScenario,
)


class SingleAgentBaseline:
    """
    Executes a benchmark scenario using one LLM call.

    This is the baseline used to compare against
    multi-agent orchestration.
    """

    def __init__(
        self,
        llm: LLMService,
    ) -> None:

        self._llm = llm

    def run(
        self,
        scenario: BenchmarkScenario,
    ) -> str:
        """
        Execute the scenario with a single LLM call.
        """

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a general-purpose "
                    "learning assistant."
                ),
            },
            {
                "role": "user",
                "content": scenario.user_request,
            },
        ]

        return self._llm.generate(
            messages,
        )