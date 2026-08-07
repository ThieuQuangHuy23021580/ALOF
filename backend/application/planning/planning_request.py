from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from backend.application.routing.routing_result import (
    RoutingResult,
)
from backend.domain.student.student import Student


class PlanningRequest(BaseModel):
    """
    Input for the planning stage.

    Encapsulates all information required by a Planner
    to generate an execution plan.
    """

    student: Student

    message: str

    routing: RoutingResult

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.metadata.get(
            key,
            default,
        )