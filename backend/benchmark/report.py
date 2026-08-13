from __future__ import annotations

from pydantic import BaseModel, Field

from backend.benchmark.comparison import BenchmarkComparison


class BenchmarkReport(BaseModel):
    """Aggregated benchmark results."""

    total_scenarios: int

    single_agent_success_rate: float

    multi_agent_success_rate: float

    single_agent_average_duration: float

    multi_agent_average_duration: float

    single_agent_average_llm_calls: float

    multi_agent_average_llm_calls: float

    comparisons: list[BenchmarkComparison] = Field(
        default_factory=list,
    )

    @classmethod
    def build(
        cls,
        comparisons: list[BenchmarkComparison],
    ) -> "BenchmarkReport":

        total = len(comparisons)

        if total == 0:
            return cls(
                total_scenarios=0,
                single_agent_success_rate=0.0,
                multi_agent_success_rate=0.0,
                single_agent_average_duration=0.0,
                multi_agent_average_duration=0.0,
                single_agent_average_llm_calls=0.0,
                multi_agent_average_llm_calls=0.0,
                comparisons=[],
            )

        single_results = [
            comparison.single_agent
            for comparison in comparisons
        ]

        multi_results = [
            comparison.multi_agent
            for comparison in comparisons
        ]

        return cls(
            total_scenarios=total,

            single_agent_success_rate=(
                sum(
                    result.success
                    for result in single_results
                )
                / total
            ),

            multi_agent_success_rate=(
                sum(
                    result.success
                    for result in multi_results
                )
                / total
            ),

            single_agent_average_duration=(
                sum(
                    result.metadata.get(
                        "duration",
                        0.0,
                    )
                    for result in single_results
                )
                / total
            ),

            multi_agent_average_duration=(
                sum(
                    result.metadata.get(
                        "duration",
                        0.0,
                    )
                    for result in multi_results
                )
                / total
            ),

            single_agent_average_llm_calls=(
                sum(
                    result.metadata.get(
                        "llm_calls",
                        0,
                    )
                    for result in single_results
                )
                / total
            ),

            multi_agent_average_llm_calls=(
                sum(
                    result.metadata.get(
                        "llm_calls",
                        0,
                    )
                    for result in multi_results
                )
                / total
            ),

            comparisons=comparisons,
        )