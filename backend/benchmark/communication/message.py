from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class BenchmarkMessage:
    sender_id: int
    receiver_id: int
    round: int
    message_type: str
    payload: dict[str, Any]