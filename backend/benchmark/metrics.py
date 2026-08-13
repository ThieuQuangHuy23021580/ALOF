from __future__ import annotations

from pydantic import BaseModel


class BenchmarkMetrics(BaseModel):
    """
    Execution metrics for one benchmark run.
    """

    duration: float

    llm_calls: int

    success: bool

    input_tokens: int | None = None

    output_tokens: int | None = None

    total_tokens: int | None = None