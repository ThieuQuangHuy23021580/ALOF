from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LLMCallMetrics:
    """
    Metrics collected for one LLM call.
    """

    stage: str | None

    component: str | None

    duration: float

    input_tokens: int

    output_tokens: int

    total_tokens: int