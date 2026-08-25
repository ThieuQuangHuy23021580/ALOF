from __future__ import annotations

from backend.benchmark.SiloBench.communication.message import (
    BenchmarkMessage,
)


class BenchmarkCommunicationBus:
    """
    In-memory communication bus for benchmark execution.

    """

    def __init__(self) -> None:
        self._messages: list[
            BenchmarkMessage
        ] = []

    def send(
        self,
        message: BenchmarkMessage,
    ) -> None:

        self._messages.append(message)

    def messages_for(
        self,
        receiver_id: int,
    ) -> list[BenchmarkMessage]:

        return [
            message
            for message in self._messages
            if message.receiver_id == receiver_id
        ]

    @property
    def messages(
        self,
    ) -> list[BenchmarkMessage]:

        return list(
            self._messages,
        )

    @property
    def message_count(
        self,
    ) -> int:

        return len(self._messages)

    def clear(self) -> None:
        self._messages.clear()