from __future__ import annotations

import json
from pathlib import Path

from backend.domain.knowledge.concept import Concept
from backend.domain.knowledge.concept_repository import (
    ConceptRepository,
)


DEFAULT_REGISTRY_PATH = (
    Path(__file__).resolve().parents[2]
    / "benchmark"
    / "ALOF"
    / "data"
    / "alof_benchmark_concept_registry_v1.json"
)


def _normalize(value: str) -> str:
    return " ".join(str(value).strip().lower().split())


class JsonConceptRepository(ConceptRepository):
    """
    Loads the existing ALOF benchmark concept registry.

    This reuses the canonical dataset vocabulary rather
    than creating a second registry.
    """

    def __init__(
        self,
        path: str | Path | None = None,
        concepts: list[Concept] | None = None,
    ) -> None:
        self._by_id: dict[str, Concept] = {}
        self._by_name: dict[str, Concept] = {}

        if concepts is not None:
            for concept in concepts:
                self._index(concept)
            return

        registry_path = Path(path) if path else DEFAULT_REGISTRY_PATH
        payload = json.loads(
            registry_path.read_text(encoding="utf-8")
        )
        for raw in payload.get("concepts", []):
            concept = self._from_registry_record(raw)
            self._index(concept)

    def get(self, concept_id: str) -> Concept | None:
        return self._by_id.get(str(concept_id).strip().lower())

    def list(self, domain: str | None = None) -> list[Concept]:
        concepts = list(self._by_id.values())
        if domain is None:
            return concepts
        normalized = _normalize(domain)
        return [
            concept
            for concept in concepts
            if _normalize(concept.domain) == normalized
        ]

    def find_by_name(self, name: str) -> Concept | None:
        return self._by_name.get(_normalize(name))

    def _index(self, concept: Concept) -> None:
        self._by_id[concept.concept_id.lower()] = concept
        self._by_name[_normalize(concept.name)] = concept
        self._by_name[_normalize(concept.concept_id)] = concept
        for alias in concept.aliases:
            self._by_name[_normalize(alias)] = concept

    @staticmethod
    def _from_registry_record(raw: dict) -> Concept:
        concept_id = str(raw.get("concept_id") or "").strip()
        name = str(
            raw.get("canonical_name")
            or raw.get("name")
            or concept_id
        ).strip()
        aliases = [
            str(item).strip()
            for item in (raw.get("aliases") or [])
            if str(item).strip()
        ]
        if name and name not in aliases:
            aliases.append(name)
        return Concept(
            concept_id=concept_id,
            name=name,
            description=str(raw.get("description") or ""),
            domain=str(raw.get("domain") or ""),
            parent_concept_id=(
                str(raw["parent_concept_id"]).strip()
                if raw.get("parent_concept_id")
                else None
            ),
            difficulty=(
                str(raw["difficulty"]).strip()
                if raw.get("difficulty")
                else None
            ),
            status=str(raw.get("status") or "active"),
            aliases=aliases,
            metadata={
                key: value
                for key, value in raw.items()
                if key
                not in {
                    "concept_id",
                    "canonical_name",
                    "name",
                    "description",
                    "domain",
                    "parent_concept_id",
                    "difficulty",
                    "status",
                    "aliases",
                }
            },
        )
