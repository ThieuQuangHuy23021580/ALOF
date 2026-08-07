from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class Parser(ABC, Generic[T]):
    """
    Generic parser contract.

    Converts raw model output into a strongly typed object.
    """

    @abstractmethod
    def parse(
        self,
        raw: str,
    ) -> T:
        raise NotImplementedError