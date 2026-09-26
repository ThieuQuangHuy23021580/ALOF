from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Protocol

from backend.config.adaptive_retrieval import AdaptiveRetrievalConfig
from backend.domain.knowledge.concept import Concept
from backend.domain.knowledge.concept_repository import (
    ConceptRepository,
)


class ConceptSemanticScorer(Protocol):
    def score(self, text: str, concept: Concept) -> float:
        ...


class ConceptLlmFallback(Protocol):
    def propose_names(self, text: str, domain: str | None) -> list[str]:
        ...


@dataclass(frozen=True)
class ConceptResolveRequest:
    text: str
    domain: str | None = None
    explicit_concept_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ConceptMatch:
    concept_id: str
    relevance: float
    source: str = "keyword"


@dataclass(frozen=True)
class ConceptResolveResult:
    concepts: list[ConceptMatch]
    candidates: list[ConceptMatch] = field(default_factory=list)


_TOKEN_RE = re.compile(r"[a-z0-9_]+", re.IGNORECASE)


def _normalize(value: str) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def _tokens(value: str) -> set[str]:
    return {
        token.lower()
        for token in _TOKEN_RE.findall(str(value or ""))
        if token
    }


class ConceptResolver:
    """
    Map task text onto canonical registry concepts.

    New canonical IDs are never created automatically.
    """

    def __init__(
        self,
        repository: ConceptRepository,
        config: AdaptiveRetrievalConfig | None = None,
        semantic_scorer: ConceptSemanticScorer | None = None,
        llm_fallback: ConceptLlmFallback | None = None,
    ) -> None:
        self._repository = repository
        self._config = config or AdaptiveRetrievalConfig()
        self._semantic_scorer = semantic_scorer
        self._llm_fallback = llm_fallback

    def resolve(
        self,
        request: ConceptResolveRequest,
    ) -> ConceptResolveResult:
        explicit = self._resolve_explicit(
            request.explicit_concept_ids
        )
        if explicit:
            return ConceptResolveResult(concepts=explicit)

        text = str(request.text or "").strip()
        if not text:
            return ConceptResolveResult(concepts=[])

        catalog = self._repository.list(request.domain)
        scored: dict[str, ConceptMatch] = {}

        exact = self._exact_canonical_match(text, catalog)
        if exact is not None:
            scored[exact.concept_id] = exact

        name_match = self._normalized_name_match(text, catalog)
        if name_match is not None:
            scored.setdefault(name_match.concept_id, name_match)

        for match in self._keyword_matches(text, catalog):
            current = scored.get(match.concept_id)
            if current is None or match.relevance > current.relevance:
                scored[match.concept_id] = match

        if self._semantic_scorer is not None:
            for match in self._semantic_matches(text, catalog):
                current = scored.get(match.concept_id)
                if current is None or match.relevance > current.relevance:
                    scored[match.concept_id] = match

        if (
            self._config.allow_llm_concept_fallback
            and self._llm_fallback is not None
            and not scored
        ):
            for match in self._llm_matches(text, request.domain, catalog):
                scored.setdefault(match.concept_id, match)

        accepted: list[ConceptMatch] = []
        candidates: list[ConceptMatch] = []
        for match in sorted(
            scored.values(),
            key=lambda item: (-item.relevance, item.concept_id),
        ):
            if match.relevance >= self._config.accept_threshold:
                accepted.append(match)
            elif match.relevance >= self._config.candidate_threshold:
                candidates.append(match)

        return ConceptResolveResult(
            concepts=accepted,
            candidates=candidates,
        )

    def resolve_target_ids(
        self,
        text: str,
        explicit_concept_ids: list[str] | None = None,
        domain: str | None = None,
    ) -> list[str]:
        result = self.resolve(
            ConceptResolveRequest(
                text=text,
                domain=domain,
                explicit_concept_ids=list(explicit_concept_ids or []),
            )
        )
        if result.concepts:
            return [match.concept_id for match in result.concepts]
        if explicit_concept_ids:
            return [
                str(value).strip()
                for value in explicit_concept_ids
                if value is not None and str(value).strip()
            ]
        return []

    def _resolve_explicit(
        self,
        concept_ids: list[str],
    ) -> list[ConceptMatch]:
        matches: list[ConceptMatch] = []
        seen: set[str] = set()
        for raw in concept_ids:
            concept_id = str(raw or "").strip()
            if not concept_id or concept_id in seen:
                continue
            seen.add(concept_id)
            registered = self._repository.get(concept_id)
            matches.append(
                ConceptMatch(
                    concept_id=(
                        registered.concept_id
                        if registered is not None
                        else concept_id
                    ),
                    relevance=1.0,
                    source="explicit",
                )
            )
        return matches

    def _exact_canonical_match(
        self,
        text: str,
        catalog: list[Concept],
    ) -> ConceptMatch | None:
        needle = _normalize(text)
        for concept in catalog:
            if needle in {
                _normalize(concept.concept_id),
                _normalize(concept.name),
            }:
                return ConceptMatch(
                    concept_id=concept.concept_id,
                    relevance=1.0,
                    source="exact",
                )
        by_id = self._repository.get(text)
        if by_id is not None:
            return ConceptMatch(
                concept_id=by_id.concept_id,
                relevance=1.0,
                source="exact",
            )
        return None

    def _normalized_name_match(
        self,
        text: str,
        catalog: list[Concept],
    ) -> ConceptMatch | None:
        needle = _normalize(text)
        for concept in catalog:
            names = [
                _normalize(concept.name),
                _normalize(concept.concept_id),
                *[_normalize(alias) for alias in concept.aliases],
            ]
            if needle in names:
                return ConceptMatch(
                    concept_id=concept.concept_id,
                    relevance=0.95,
                    source="name",
                )
            if any(
                name and (name in needle or needle in name)
                for name in names
            ):
                return ConceptMatch(
                    concept_id=concept.concept_id,
                    relevance=0.85,
                    source="name",
                )
        found = self._repository.find_by_name(text)
        if found is not None:
            return ConceptMatch(
                concept_id=found.concept_id,
                relevance=0.95,
                source="name",
            )
        return None

    def _keyword_matches(
        self,
        text: str,
        catalog: list[Concept],
    ) -> list[ConceptMatch]:
        query_tokens = _tokens(text) | set(_normalize(text).split("_"))
        query_tokens.discard("")
        if not query_tokens:
            return []

        matches: list[ConceptMatch] = []
        for concept in catalog:
            concept_tokens = (
                _tokens(concept.concept_id)
                | _tokens(concept.name)
                | _tokens(concept.description)
                | set(_normalize(concept.concept_id).split("_"))
            )
            concept_tokens.discard("")
            if not concept_tokens:
                continue
            overlap = query_tokens & concept_tokens
            if not overlap:
                continue
            relevance = len(overlap) / max(len(concept_tokens), 1)
            matches.append(
                ConceptMatch(
                    concept_id=concept.concept_id,
                    relevance=min(1.0, relevance),
                    source="keyword",
                )
            )
        return matches

    def _semantic_matches(
        self,
        text: str,
        catalog: list[Concept],
    ) -> list[ConceptMatch]:
        matches: list[ConceptMatch] = []
        scorer = self._semantic_scorer
        if scorer is None:
            return matches
        for concept in catalog:
            score = max(0.0, min(1.0, float(scorer.score(text, concept))))
            if score <= 0.0:
                continue
            matches.append(
                ConceptMatch(
                    concept_id=concept.concept_id,
                    relevance=score,
                    source="semantic",
                )
            )
        return matches

    def _llm_matches(
        self,
        text: str,
        domain: str | None,
        catalog: list[Concept],
    ) -> list[ConceptMatch]:
        if self._llm_fallback is None:
            return []
        proposed = self._llm_fallback.propose_names(text, domain)
        catalog_by_id = {
            concept.concept_id.lower(): concept
            for concept in catalog
        }
        matches: list[ConceptMatch] = []
        for name in proposed:
            normalized = _normalize(name)
            concept = self._repository.find_by_name(name)
            if concept is None:
                concept = catalog_by_id.get(normalized)
            if concept is None:
                continue
            matches.append(
                ConceptMatch(
                    concept_id=concept.concept_id,
                    relevance=self._config.accept_threshold,
                    source="llm",
                )
            )
        return matches
