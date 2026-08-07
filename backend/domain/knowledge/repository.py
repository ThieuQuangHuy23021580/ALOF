from __future__ import annotations

from abc import ABC, abstractmethod

from backend.domain.knowledge.knowledge_node import (
    KnowledgeNode,
)


class KnowledgeRepository(ABC):
    """
    Domain repository for KnowledgeNode Aggregate.

    Infrastructure implementations (SQLite, PostgreSQL,
    MongoDB, Neo4j, etc.) must implement this contract.
    """

    @abstractmethod
    def add(
        self,
        knowledge: KnowledgeNode,
    ) -> None:
        """
        Persist a new knowledge node.
        """
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        knowledge_id: str,
    ) -> KnowledgeNode | None:
        """
        Retrieve a knowledge node by id.
        """
        raise NotImplementedError

    @abstractmethod
    def list(
        self,
    ) -> list[KnowledgeNode]:
        """
        Retrieve all knowledge nodes.
        """
        raise NotImplementedError

    @abstractmethod
    def remove(
        self,
        knowledge_id: str,
    ) -> None:
        """
        Remove a knowledge node.
        """
        raise NotImplementedError