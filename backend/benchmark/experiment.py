from __future__ import annotations

from time import perf_counter

from backend.application.services.llm_service import (
    LLMService,
)
from backend.benchmark.multi_agent import (
    MultiAgentBaseline,
)
from backend.benchmark.result import (
    BenchmarkResult,
)
from backend.benchmark.scenario import (
    BenchmarkScenario,
)
from backend.benchmark.single_agent import (
    SingleAgentBaseline,
)


class BenchmarkExperiment:
    """
    Runs the same benchmark scenario using
    different execution approaches.
    """

    def __init__(
        self,
        llm: LLMService,
    ) -> None:

        self._llm = llm

    def run_single_agent(
        self,
        scenario: BenchmarkScenario,
    ) -> BenchmarkResult:

        start = perf_counter()

        try:

            baseline = SingleAgentBaseline(
                llm=self._llm,
            )

            output = baseline.run(
                scenario,
            )

            success = True

        except Exception:

            output = None

            success = False

        duration = (
            perf_counter()
            - start
        )

        return BenchmarkResult(
            scenario_id=scenario.id,
            approach="single_agent",
            success=success,
            output=output,
            metadata={
                "duration": duration,
            },
        )

    def run_multi_agent(
        self,
        scenario: BenchmarkScenario,
    ) -> BenchmarkResult:

        start = perf_counter()

        try:

            baseline = MultiAgentBaseline(
                llm=self._llm,
            )

            result = baseline.run(
                scenario,
            )

            output = None

            if result.final_artifact is not None:

                output = (
                    result.final_artifact.content
                )

            success = (
                result.status.value
                == "completed"
            )

        except Exception:

            result = None

            output = None

            success = False

        duration = (
            perf_counter()
            - start
        )

        return BenchmarkResult(
            scenario_id=scenario.id,
            approach="multi_agent",
            success=success,
            output=output,
            metadata={
                "duration": duration,
                "execution_order": (
                    result.execution_order
                    if result is not None
                    else []
                ),
            },
        )