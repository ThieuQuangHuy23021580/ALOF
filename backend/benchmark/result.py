from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BenchmarkResult(BaseModel):
    """
    Normalized result of one benchmark execution.

    This model contains benchmark outcome data only.
    Metrics are added in a later step.
    """

    scenario_id: str

    approach: str

    success: bool

    output: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )