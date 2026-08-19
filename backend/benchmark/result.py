from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BenchmarkResult(BaseModel):
    """
    Standard result produced by a benchmark runner.

    This model is independent from any specific benchmark
    implementation such as SILO-BENCH.
    """

    scenario_id: str

    scenario_name: str

    success: bool

    agent_count: int

    duration_seconds: float

    component_calls: int = 0

    rounds: int = 0

    llm_calls: int = 0

    input_tokens: int = 0

    output_tokens: int = 0

    total_tokens: int = 0

    communication_messages: int = 0

    metrics: dict[str, float] = Field(
        default_factory=dict,
    )

    details: dict[str, Any] = Field(
        default_factory=dict,
    )