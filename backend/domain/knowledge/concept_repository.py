from __future__ import annotations

from abc import ABC, abstractmethod

from backend.domain.knowledge.concept import Concept


class ConceptRepository(ABC):
    """Canonical concept registry contract."""

    @abstractmethod
    def get(self, concept_id: str) -> Concept | None:
        raise NotImplementedError

    @abstractmethod
    def list(self, domain: str | None = None) -> list[Concept]:
        raise NotImplementedError

    @abstractmethod
    def find_by_name(self, name: str) -> Concept | None:
        raise NotImplementedError
