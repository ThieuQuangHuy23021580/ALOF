from __future__ import annotations

import os
from dataclasses import dataclass, field, replace


RETRIEVAL_WEIGHT_PRESETS: dict[str, dict[str, float]] = {
    "A": {
        "concept": 0.0,
        "error": 0.0,
        "recency": 1.0,
        "semantic": 0.0,
    },
    "B": {
        "concept": 1.0,
        "error": 0.0,
        "recency": 0.0,
        "semantic": 0.0,
    },
    "C": {
        "concept": 0.62,
        "error": 0.38,
        "recency": 0.0,
        "semantic": 0.0,
    },
    "D": {
        "concept": 0.47,
        "error": 0.29,
        "recency": 0.24,
        "semantic": 0.0,
    },
    "E": {
        "concept": 0.40,
        "error": 0.25,
        "recency": 0.20,
        "semantic": 0.15,
    },
}


DEFAULT_RETRIEVAL_WEIGHTS: dict[str, float] = dict(
    RETRIEVAL_WEIGHT_PRESETS["E"]
)


def _env_bool(
    name: str,
    default: bool,
) -> bool:
    raw = os.environ.get(name)

    if raw is None:
        return default

    return raw.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _env_float(
    name: str,
    default: float,
) -> float:
    raw = os.environ.get(name)

    if raw is None or not raw.strip():
        return default

    return float(raw)


def _env_int(
    name: str,
    default: int,
) -> int:
    raw = os.environ.get(name)

    if raw is None or not raw.strip():
        return default

    return int(raw)


def _env_str(
    name: str,
    default: str,
) -> str:
    raw = os.environ.get(name)

    if raw is None or not raw.strip():
        return default

    return raw.strip()


@dataclass(frozen=True)
class AdaptiveRetrievalConfig:
    enabled: bool = True
    trace_enabled: bool = False

    top_k: int = 5
    candidate_limit: int = 50

    recency_decay: float = 0.1
    recency_unit_seconds: float = 86400.0

    accept_threshold: float = 0.75
    candidate_threshold: float = 0.50

    confidence_k: float = 5.0

    weakness_threshold: float = 0.5
    beginner_mastery_threshold: float = 0.4
    advanced_mastery_threshold: float = 0.7

    retrieval_profile: str = "E"
    retrieval_weights: dict[str, float] = field(
        default_factory=lambda: dict(
            DEFAULT_RETRIEVAL_WEIGHTS
        )
    )

    allow_llm_concept_fallback: bool = False
    allow_new_concepts: bool = False

    def with_updates(
        self,
        **changes: object,
    ) -> AdaptiveRetrievalConfig:
        return replace(
            self,
            **changes,
        )


def _weights_from_env(
    profile: str,
) -> dict[str, float]:

    normalized_profile = profile.upper()

    preset = RETRIEVAL_WEIGHT_PRESETS.get(
        normalized_profile,
        DEFAULT_RETRIEVAL_WEIGHTS,
    )

    weights = dict(preset)

    weights["concept"] = _env_float(
        "RETRIEVAL_WEIGHT_CONCEPT",
        weights["concept"],
    )

    weights["error"] = _env_float(
        "RETRIEVAL_WEIGHT_ERROR",
        weights["error"],
    )

    weights["recency"] = _env_float(
        "RETRIEVAL_WEIGHT_RECENCY",
        weights["recency"],
    )

    weights["semantic"] = _env_float(
        "RETRIEVAL_WEIGHT_SEMANTIC",
        weights["semantic"],
    )

    if any(
        value < 0.0
        for value in weights.values()
    ):
        raise ValueError(
            "Retrieval weights must be non-negative."
        )

    if sum(weights.values()) <= 0.0:
        raise ValueError(
            "At least one retrieval weight must be greater than zero."
        )

    return weights


def load_adaptive_retrieval_config() -> AdaptiveRetrievalConfig:
    profile = _env_str(
        "RETRIEVAL_PROFILE",
        "E",
    ).upper()

    top_k = _env_int(
        "ADAPTIVE_RETRIEVAL_TOP_K",
        5,
    )

    candidate_limit = _env_int(
        "ADAPTIVE_RETRIEVAL_CANDIDATE_LIMIT",
        50,
    )

    if top_k <= 0:
        raise ValueError(
            "ADAPTIVE_RETRIEVAL_TOP_K must be greater than zero."
        )

    if candidate_limit <= 0:
        raise ValueError(
            "ADAPTIVE_RETRIEVAL_CANDIDATE_LIMIT must be greater than zero."
        )

    recency_decay = _env_float(
        "RECENCY_DECAY",
        0.1,
    )

    recency_unit_seconds = _env_float(
        "RECENCY_UNIT_SECONDS",
        86400.0,
    )

    if recency_decay < 0.0:
        raise ValueError(
            "RECENCY_DECAY must be non-negative."
        )

    if recency_unit_seconds <= 0.0:
        raise ValueError(
            "RECENCY_UNIT_SECONDS must be greater than zero."
        )

    candidate_threshold = _env_float(
        "CONCEPT_CANDIDATE_THRESHOLD",
        0.50,
    )

    accept_threshold = _env_float(
        "CONCEPT_ACCEPT_THRESHOLD",
        0.75,
    )

    if not 0.0 <= candidate_threshold <= 1.0:
        raise ValueError(
            "CONCEPT_CANDIDATE_THRESHOLD must be between 0 and 1."
        )

    if not 0.0 <= accept_threshold <= 1.0:
        raise ValueError(
            "CONCEPT_ACCEPT_THRESHOLD must be between 0 and 1."
        )

    return AdaptiveRetrievalConfig(
        enabled=_env_bool(
            "ADAPTIVE_RETRIEVAL_ENABLED",
            True,
        ),
        trace_enabled=_env_bool(
            "ADAPTIVE_RETRIEVAL_TRACE_ENABLED",
            False,
        ),
        top_k=top_k,
        candidate_limit=candidate_limit,
        recency_decay=recency_decay,
        recency_unit_seconds=recency_unit_seconds,
        accept_threshold=accept_threshold,
        candidate_threshold=candidate_threshold,
        confidence_k=_env_float(
            "DIAGNOSIS_CONFIDENCE_K",
            5.0,
        ),
        weakness_threshold=_env_float(
            "WEAKNESS_THRESHOLD",
            0.5,
        ),
        beginner_mastery_threshold=_env_float(
            "BEGINNER_MASTERY_THRESHOLD",
            0.4,
        ),
        advanced_mastery_threshold=_env_float(
            "ADVANCED_MASTERY_THRESHOLD",
            0.7,
        ),
        retrieval_profile=profile,
        retrieval_weights=_weights_from_env(
            profile,
        ),
        allow_llm_concept_fallback=_env_bool(
            "CONCEPT_LLM_FALLBACK_ENABLED",
            False,
        ),
        allow_new_concepts=_env_bool(
            "CONCEPT_ALLOW_CREATE",
            False,
        ),
    )