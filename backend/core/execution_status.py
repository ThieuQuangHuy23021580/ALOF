from __future__ import annotations

from enum import Enum


class ExecutionStatus(str, Enum):
    """
    Common execution status shared across the framework.
    """

    CREATED = "created"

    READY = "ready"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    CANCELLED = "cancelled"

    SKIPPED = "skipped"

    PAUSED = "paused"