from __future__ import annotations

from abc import ABC, abstractmethod

from backend.domain.artifact.artifact import Artifact


class ArtifactRepository(ABC):
    """
    Domain repository for Artifact Aggregate.

    This interface belongs to the Domain Layer.

    Infrastructure implementations (SQLite, PostgreSQL,
    MongoDB, etc.) must implement this contract.
    """

    @abstractmethod
    def add(
        self,
        artifact: Artifact,
    ) -> None:
        """
        Persist a new artifact.
        """
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        artifact_id: str,
    ) -> Artifact | None:
        """
        Retrieve an artifact by id.
        """
        raise NotImplementedError

    @abstractmethod
    def list(
        self,
    ) -> list[Artifact]:
        """
        Retrieve all artifacts.
        """
        raise NotImplementedError

    @abstractmethod
    def remove(
        self,
        artifact_id: str,
    ) -> None:
        """
        Remove an artifact.
        """
        raise NotImplementedError