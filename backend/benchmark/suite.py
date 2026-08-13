from __future__ import annotations

from backend.benchmark.comparison import (
    BenchmarkComparison,
)
from backend.benchmark.experiment import (
    BenchmarkExperiment,
)
from backend.benchmark.scenario import (
    BenchmarkScenario,
)


class BenchmarkSuite:
    """
    Runs a collection of benchmark scenarios
    using both Single-Agent and Multi-Agent approaches.
    """

    def __init__(
        self,
        experiment: BenchmarkExperiment,
    ) -> None:

        self._experiment = experiment

    def run(
        self,
        scenarios: list[BenchmarkScenario],
    ) -> list[BenchmarkComparison]:

        comparisons: list[
            BenchmarkComparison
        ] = []

        for scenario in scenarios:

            single_result = (
                self._experiment.run_single_agent(
                    scenario,
                )
            )

            multi_result = (
                self._experiment.run_multi_agent(
                    scenario,
                )
            )

            comparison = BenchmarkComparison(
                single_agent=single_result,
                multi_agent=multi_result,
            )

            comparisons.append(
                comparison,
            )

        return comparisons