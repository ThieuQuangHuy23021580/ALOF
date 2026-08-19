from __future__ import annotations

from typing import Any

from .communication_event import CommunicationEvent


class CommunicationTrace:
    """
    Records communication events during a benchmark run.

    This class is intentionally independent from any
    particular benchmark case.
    """

    def __init__(self) -> None:

        self._events: list[
            CommunicationEvent
        ] = []

    def record(
        self,
        *,
        sender: int,
        receiver: int,
        round: int,
        message_type: str,
        payload: Any = None,
    ) -> None:

        self._events.append(
            CommunicationEvent(
                sender=sender,
                receiver=receiver,
                round=round,
                message_type=message_type,
                payload=payload,
            )
        )

    @property
    def events(
        self,
    ) -> list[CommunicationEvent]:

        return list(
            self._events
        )

    @property
    def message_count(
        self,
    ) -> int:

        return len(
            self._events
        )

    @property
    def rounds(
        self,
    ) -> int:

        if not self._events:
            return 0

        return len(
            {
                event.round
                for event in self._events
            }
        )

    @property
    def edges(
        self,
    ) -> set[tuple[int, int]]:

        return {
            (
                event.sender,
                event.receiver,
            )
            for event in self._events
        }