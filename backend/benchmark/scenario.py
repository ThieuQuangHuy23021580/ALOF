from __future__ import annotations

from pydantic import BaseModel, Field


class BenchmarkScenario(BaseModel):
    """
    Defines one benchmark scenario for ALOF.

    A scenario describes what should be executed,
    but does not execute anything itself.
    """

    id: str

    name: str

    user_request: str

    component_ids: list[str] = Field(
        default_factory=list,
    )

    expected_output: str

    metadata: dict[str, str] = Field(
        default_factory=dict,
    )