from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BenchmarkResult(BaseModel):
    """
    Structured result produced by a benchmark run.
    """

    scenario: str

    status: str

    duration: float | None = None

    llm_calls: int = 0

    intents: list[str] = Field(
        default_factory=list,
    )

    candidate_components: list[str] = Field(
        default_factory=list,
    )

    execution_order: list[str] = Field(
        default_factory=list,
    )

    plan: list[dict[str, Any]] = Field(
        default_factory=list,
    )

    artifacts: list[dict[str, Any]] = Field(
        default_factory=list,
    )

    final_artifact: dict[str, Any] | None = None