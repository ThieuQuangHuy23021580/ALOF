from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CommunicationEvent:
    """
    One logical message exchanged between two agents.
    """

    sender: int

    receiver: int

    round: int

    message_type: str

    payload: Any = None