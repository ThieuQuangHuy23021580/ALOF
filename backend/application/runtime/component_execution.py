from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel

from backend.core.execution_status import ExecutionStatus


class ComponentExecution(BaseModel):
    """
    Runtime record of one Component execution.
    """

    component_id: str

    node_id: str

    status: ExecutionStatus = (
        ExecutionStatus.CREATED
    )

    started_at: datetime | None = None

    finished_at: datetime | None = None

    error: str | None = None

    metadata: dict[str, Any] = {}

    def start(
        self,
    ) -> None:

        self.status = ExecutionStatus.RUNNING

        self.started_at = datetime.now(
            UTC,
        )

    def complete(
        self,
    ) -> None:

        self.status = ExecutionStatus.COMPLETED

        self.finished_at = datetime.now(
            UTC,
        )

    def fail(
        self,
        error: str,
    ) -> None:

        self.status = ExecutionStatus.FAILED

        self.error = error

        self.finished_at = datetime.now(
            UTC,
        )

    def duration(
        self,
    ) -> float | None:

        if (
            self.started_at is None
            or self.finished_at is None
        ):
            return None

        return (
            self.finished_at
            - self.started_at
        ).total_seconds()