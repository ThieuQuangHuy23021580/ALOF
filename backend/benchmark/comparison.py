from __future__ import annotations

from dataclasses import dataclass

from backend.benchmark.result import BenchmarkResult


@dataclass(frozen=True)
class BenchmarkComparison:
    """
    Comparison between Single-Agent and Multi-Agent results.
    """

    single_agent: BenchmarkResult
    multi_agent: BenchmarkResult

    @property
    def single_success(self) -> bool:
        return self.single_agent.success

    @property
    def multi_success(self) -> bool:
        return self.multi_agent.success

    @property
    def single_duration(self) -> float:
        return float(
            self.single_agent.metadata.get(
                "duration",
                0.0,
            )
        )

    @property
    def multi_duration(self) -> float:
        return float(
            self.multi_agent.metadata.get(
                "duration",
                0.0,
            )
        )

    @property
    def single_llm_calls(self) -> int:
        return int(
            self.single_agent.metadata.get(
                "llm_calls",
                0,
            )
        )

    @property
    def multi_llm_calls(self) -> int:
        return int(
            self.multi_agent.metadata.get(
                "llm_calls",
                0,
            )
        )

    @property
    def multi_agent_success_advantage(self) -> bool:
        return (
            self.multi_success
            and not self.single_success
        )

    @property
    def duration_difference(self) -> float:
        return (
            self.multi_duration
            - self.single_duration
        )