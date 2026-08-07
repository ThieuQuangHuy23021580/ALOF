from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol, TypeVar, runtime_checkable

ContextT = TypeVar("ContextT")
ArtifactT = TypeVar("ArtifactT")


@runtime_checkable
class Executable(Protocol[ContextT, ArtifactT]):
    """
    Any executable component inside ALOF.
    """

    def invoke(
        self,
        context: ContextT,
    ) -> ArtifactT:
        ...


@runtime_checkable
class Registrable(Protocol):
    """
    Object that can be registered inside Registry.
    """

    @property
    def component_id(self) -> str:
        ...

    @property
    def name(self) -> str:
        ...


class SupportsInitialize(ABC):
    """
    Optional lifecycle.
    """

    @abstractmethod
    def initialize(self) -> None:
        ...


class SupportsShutdown(ABC):
    """
    Optional lifecycle.
    """

    @abstractmethod
    def shutdown(self) -> None:
        ...


class SupportsHealthCheck(ABC):
    """
    Infrastructure health checking.
    """

    @abstractmethod
    def health_check(self) -> bool:
        ...