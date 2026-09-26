from __future__ import annotations

from datetime import UTC, datetime
from math import exp
from typing import Any

from backend.config.adaptive_retrieval import (
    AdaptiveRetrievalConfig,
    load_adaptive_retrieval_config,
)
from backend.domain.learning.historical_evidence import (
    HistoricalEvidence,
)
from backend.domain.learning.learning_interaction import (
    LearningInteraction,
)
from backend.domain.learning.learning_state import (
    LearningState,
)


class HistoricalEvidenceBuilder:
    """
    Build adaptive historical evidence for ALOF.

    Responsibilities
    ----------------
    - Preserve native LearningState interactions.
    - Normalize external history into LearningInteraction.
    - Rank evidence using adaptive retrieval signals.
    - Keep recent, relevant, and related evidence separate.
    - Preserve deterministic retrieval behavior.
    - Prevent benchmark Gold annotations from entering evidence.

    Retrieval signals
    -----------------
    - concept relevance
    - error relevance
    - recency
    - lexical question relevance

    This component does NOT:
    - perform diagnosis;
    - call an LLM;
    - access Gold answers;
    - modify LearningState.
    """

    _GOLD_FIELDS = {
        "gold_memory_queries",
        "gold_answer",
        "gold_answers",
    }

    _METADATA_FIELDS = {
        "_key",
        "record_id",
        "event_id",
        "question_id",
        "questionId",
        "qid",
        "id",
        "question",
        "question_text",
        "questionText",
        "content",
        "problem",
        "answer",
        "student_answer",
        "studentAnswer",
        "response",
        "correct",
        "is_correct",
        "isCorrect",
        "result",
        "concept_ids",
        "conceptIds",
        "concepts",
        "timestamp",
        "created_at",
        "createdAt",
        "time",
        "datetime",
        "source",
        "evidence_source",
        "history_source",
        "related",
        "related_history",
    }

    def __init__(
        self,
        recent_limit: int = 5,
        config: AdaptiveRetrievalConfig | None = None,
    ) -> None:

        if recent_limit <= 0:
            raise ValueError(
                "recent_limit must be greater than 0."
            )

        self._recent_limit = recent_limit

        self._config = (
            config
            if config is not None
            else load_adaptive_retrieval_config()
        )

    def build(
        self,
        learning_state: LearningState,
        current_question: str = "",
        related_concept_ids: list[str] | None = None,
        history_info: list[Any] | None = None,
        related_history: list[Any] | None = None,
    ) -> HistoricalEvidence:

        interactions = list(
            learning_state.interactions
        )

        relevant_concepts = {
            str(value)
            for value in (related_concept_ids or [])
            if value is not None
        }

        evidence = HistoricalEvidence(
            learner_id=learning_state.learner_id,
            current_question=current_question,
        )

        # ==================================================
        # Recent evidence
        # ==================================================

        recent_interactions = sorted(
            interactions,
            key=lambda interaction: interaction.timestamp,
        )[-self._recent_limit:]

        for interaction in recent_interactions:
            evidence.add_recent_interaction(
                interaction,
            )

            for concept_id in interaction.concept_ids:
                evidence.add_related_concept(
                    str(concept_id),
                )

        # ==================================================
        # Normalize external history
        # ==================================================

        external_history: list[
            LearningInteraction
        ] = []

        external_related_history: list[
            LearningInteraction
        ] = []

        for record in history_info or []:
            interaction = self._to_learning_interaction(
                record=record,
                learner_id=learning_state.learner_id,
                source="history_info",
            )

            if interaction is not None:
                external_history.append(
                    interaction
                )

        for record in related_history or []:
            interaction = self._to_learning_interaction(
                record=record,
                learner_id=learning_state.learner_id,
                source="related_history",
            )

            if interaction is not None:
                external_related_history.append(
                    interaction
                )

        # ==================================================
        # Adaptive retrieval
        # ==================================================

        native_ranked = self._rank_interactions(
            interactions=interactions,
            current_question=current_question,
            relevant_concepts=relevant_concepts,
        )

        external_ranked = self._rank_interactions(
            interactions=(
                external_history
                + external_related_history
            ),
            current_question=current_question,
            relevant_concepts=relevant_concepts,
        )

        if self._config.enabled:

            for interaction, score in native_ranked[
                : self._config.top_k
            ]:

                if score < self._config.candidate_threshold:
                    continue

                evidence.add_relevant_interaction(
                    interaction,
                )

                for concept_id in interaction.concept_ids:
                    evidence.add_related_concept(
                        str(concept_id),
                    )

            for interaction, score in external_ranked[
                : self._config.top_k
            ]:

                if score < self._config.candidate_threshold:
                    continue

                source = str(
                    interaction.metadata.get(
                        "evidence_source",
                        "history_info",
                    )
                )

                if source == "related_history":
                    evidence.add_related_interaction(
                        interaction,
                    )
                else:
                    evidence.add_relevant_interaction(
                        interaction,
                    )

                for concept_id in interaction.concept_ids:
                    evidence.add_related_concept(
                        str(concept_id),
                    )

        else:

            self._build_legacy_relevant_evidence(
                evidence=evidence,
                interactions=interactions,
                relevant_concepts=relevant_concepts,
            )

            for interaction in external_history:
                evidence.add_relevant_interaction(
                    interaction,
                )

                for concept_id in interaction.concept_ids:
                    evidence.add_related_concept(
                        str(concept_id),
                    )

            for interaction in external_related_history:
                evidence.add_related_interaction(
                    interaction,
                )

                for concept_id in interaction.concept_ids:
                    evidence.add_related_concept(
                        str(concept_id),
                    )

        # ==================================================
        # Metadata
        # ==================================================

        evidence.set_metadata(
            "selection_strategy",
            (
                "adaptive_hybrid_retrieval"
                if self._config.enabled
                else "recent_and_relevant_with_related_external_history"
            ),
        )

        evidence.set_metadata(
            "adaptive_retrieval_enabled",
            self._config.enabled,
        )

        evidence.set_metadata(
            "retrieval_profile",
            self._config.retrieval_profile,
        )

        evidence.set_metadata(
            "recent_limit",
            self._recent_limit,
        )

        evidence.set_metadata(
            "top_k",
            self._config.top_k,
        )

        evidence.set_metadata(
            "candidate_limit",
            self._config.candidate_limit,
        )

        evidence.set_metadata(
            "candidate_threshold",
            self._config.candidate_threshold,
        )

        evidence.set_metadata(
            "source_interaction_count",
            len(interactions),
        )

        evidence.set_metadata(
            "recent_interaction_count",
            len(evidence.recent_interactions),
        )

        evidence.set_metadata(
            "relevant_interaction_count",
            len(evidence.relevant_interactions),
        )

        evidence.set_metadata(
            "related_interaction_count",
            len(evidence.related_interactions),
        )

        evidence.set_metadata(
            "external_history_count",
            len(external_history),
        )

        evidence.set_metadata(
            "external_related_history_count",
            len(external_related_history),
        )

        evidence.set_metadata(
            "external_evidence_count",
            (
                len(external_history)
                + len(external_related_history)
            ),
        )

        evidence.set_metadata(
            "retrieval_candidate_count",
            len(interactions)
            + len(external_history)
            + len(external_related_history),
        )

        evidence.set_metadata(
            "retrieval_selected_count",
            (
                len(evidence.relevant_interactions)
                + len(evidence.related_interactions)
            ),
        )

        evidence.set_metadata(
            "retrieval_weights",
            dict(
                self._normalized_weights()
            ),
        )

        if self._config.trace_enabled:
            evidence.set_metadata(
                "retrieval_trace",
                self._build_trace(
                    native_ranked=native_ranked,
                    external_ranked=external_ranked,
                    current_question=current_question,
                    relevant_concepts=relevant_concepts,
                ),
            )

        return evidence

    # ======================================================
    # Legacy retrieval
    # ======================================================

    def _build_legacy_relevant_evidence(
        self,
        evidence: HistoricalEvidence,
        interactions: list[LearningInteraction],
        relevant_concepts: set[str],
    ) -> None:

        if not relevant_concepts:
            return

        for interaction in interactions:

            interaction_concepts = {
                str(value)
                for value in interaction.concept_ids
            }

            if relevant_concepts.intersection(
                interaction_concepts
            ):
                evidence.add_relevant_interaction(
                    interaction,
                )

                for concept_id in interaction.concept_ids:
                    evidence.add_related_concept(
                        str(concept_id),
                    )

    # ======================================================
    # Adaptive ranking
    # ======================================================

    def _rank_interactions(
        self,
        interactions: list[LearningInteraction],
        current_question: str,
        relevant_concepts: set[str],
    ) -> list[
        tuple[LearningInteraction, float]
    ]:

        if not interactions:
            return []

        unique: dict[str, LearningInteraction] = {}

        for interaction in interactions:
            unique.setdefault(
                interaction.id,
                interaction,
            )

        candidates = list(
            unique.values()
        )

        candidates.sort(
            key=lambda interaction: (
                interaction.timestamp,
            ),
            reverse=True,
        )

        candidates = candidates[
            : self._config.candidate_limit
        ]

        latest_timestamp = max(
            (
                interaction.timestamp
                for interaction in candidates
            ),
            default=datetime.fromtimestamp(
                0,
                tz=UTC,
            ),
        )

        weights = self._normalized_weights()

        scored: list[
            tuple[LearningInteraction, float]
        ] = []

        for interaction in candidates:

            concept_score = (
                self._concept_relevance(
                    interaction=interaction,
                    relevant_concepts=relevant_concepts,
                )
            )

            error_score = (
                self._error_relevance(
                    interaction=interaction,
                )
            )

            recency_score = (
                self._recency_score(
                    timestamp=interaction.timestamp,
                    latest_timestamp=latest_timestamp,
                )
            )

            semantic_score = (
                self._semantic_relevance(
                    current_question=current_question,
                    historical_question=interaction.question,
                )
            )

            score = (
                weights["concept"]
                * concept_score
                + weights["error"]
                * error_score
                + weights["recency"]
                * recency_score
                + weights["semantic"]
                * semantic_score
            )

            scored.append(
                (
                    interaction,
                    score,
                )
            )

        scored.sort(
            key=lambda item: (
                item[1],
                item[0].timestamp,
            ),
            reverse=True,
        )

        return scored

    def _normalized_weights(
        self,
    ) -> dict[str, float]:

        weights = {
            "concept": float(
                self._config.retrieval_weights.get(
                    "concept",
                    0.0,
                )
            ),
            "error": float(
                self._config.retrieval_weights.get(
                    "error",
                    0.0,
                )
            ),
            "recency": float(
                self._config.retrieval_weights.get(
                    "recency",
                    0.0,
                )
            ),
            "semantic": float(
                self._config.retrieval_weights.get(
                    "semantic",
                    0.0,
                )
            ),
        }

        total = sum(
            weights.values()
        )

        if total <= 0.0:
            return {
                "concept": 0.0,
                "error": 0.0,
                "recency": 1.0,
                "semantic": 0.0,
            }

        return {
            key: value / total
            for key, value in weights.items()
        }

    # ======================================================
    # Retrieval signals
    # ======================================================

    @staticmethod
    def _concept_relevance(
        interaction: LearningInteraction,
        relevant_concepts: set[str],
    ) -> float:

        if not relevant_concepts:
            return 0.0

        interaction_concepts = {
            str(value)
            for value in interaction.concept_ids
        }

        if not interaction_concepts:
            return 0.0

        overlap = (
            relevant_concepts
            .intersection(
                interaction_concepts
            )
        )

        if not overlap:
            return 0.0

        return min(
            1.0,
            len(overlap)
            / len(relevant_concepts),
        )

    @staticmethod
    def _error_relevance(
        interaction: LearningInteraction,
    ) -> float:

        if interaction.correct is False:
            return 1.0

        if interaction.correct is True:
            return 0.0

        return 0.5

    def _recency_score(
        self,
        timestamp: datetime,
        latest_timestamp: datetime,
    ) -> float:

        if timestamp >= latest_timestamp:
            return 1.0

        age_seconds = (
            latest_timestamp
            - timestamp
        ).total_seconds()

        if age_seconds <= 0.0:
            return 1.0

        units = (
            age_seconds
            / self._config.recency_unit_seconds
        )

        return exp(
            -self._config.recency_decay
            * units
        )

    @staticmethod
    def _semantic_relevance(
        current_question: str,
        historical_question: str,
    ) -> float:

        current_tokens = (
            HistoricalEvidenceBuilder._tokenize(
                current_question,
            )
        )

        historical_tokens = (
            HistoricalEvidenceBuilder._tokenize(
                historical_question,
            )
        )

        if (
            not current_tokens
            or not historical_tokens
        ):
            return 0.0

        intersection = (
            current_tokens
            .intersection(
                historical_tokens
            )
        )

        union = (
            current_tokens
            .union(
                historical_tokens
            )
        )

        if not union:
            return 0.0

        return (
            len(intersection)
            / len(union)
        )

    @staticmethod
    def _tokenize(
        text: str,
    ) -> set[str]:

        if not text:
            return set()

        normalized = (
            text.lower()
            .replace("?", " ")
            .replace(",", " ")
            .replace(".", " ")
            .replace(":", " ")
            .replace(";", " ")
            .replace("(", " ")
            .replace(")", " ")
            .replace("[", " ")
            .replace("]", " ")
            .replace("{", " ")
            .replace("}", " ")
        )

        return {
            token
            for token in normalized.split()
            if len(token) > 1
        }

    # ======================================================
    # Retrieval trace
    # ======================================================

    def _build_trace(
        self,
        native_ranked: list[
            tuple[LearningInteraction, float]
        ],
        external_ranked: list[
            tuple[LearningInteraction, float]
        ],
        current_question: str,
        relevant_concepts: set[str],
    ) -> list[dict[str, Any]]:

        weights = self._normalized_weights()

        trace: list[dict[str, Any]] = []

        latest_candidates = (
            native_ranked
            + external_ranked
        )

        latest_timestamp = max(
            (
                interaction.timestamp
                for interaction, _ in latest_candidates
            ),
            default=datetime.fromtimestamp(
                0,
                tz=UTC,
            ),
        )

        seen: set[str] = set()

        for interaction, score in (
            latest_candidates
        ):

            if interaction.id in seen:
                continue

            seen.add(
                interaction.id
            )

            concept_score = (
                self._concept_relevance(
                    interaction,
                    relevant_concepts,
                )
            )

            error_score = (
                self._error_relevance(
                    interaction,
                )
            )

            recency_score = (
                self._recency_score(
                    interaction.timestamp,
                    latest_timestamp,
                )
            )

            semantic_score = (
                self._semantic_relevance(
                    current_question,
                    interaction.question,
                )
            )

            trace.append(
                {
                    "interaction_id": interaction.id,
                    "question_id": interaction.question_id,
                    "score": score,
                    "concept_score": concept_score,
                    "error_score": error_score,
                    "recency_score": recency_score,
                    "semantic_score": semantic_score,
                    "weighted_concept": (
                        weights["concept"]
                        * concept_score
                    ),
                    "weighted_error": (
                        weights["error"]
                        * error_score
                    ),
                    "weighted_recency": (
                        weights["recency"]
                        * recency_score
                    ),
                    "weighted_semantic": (
                        weights["semantic"]
                        * semantic_score
                    ),
                }
            )

        trace.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return trace

    # ======================================================
    # External history normalization
    # ======================================================

    def _to_learning_interaction(
        self,
        record: Any,
        learner_id: str,
        source: str,
    ) -> LearningInteraction | None:

        data = self._normalize_record(
            record,
        )

        if not data:
            return None

        question_id = self._first_value(
            data,
            "question_id",
            "questionId",
            "qid",
            "id",
        )

        question = self._first_value(
            data,
            "question",
            "question_text",
            "questionText",
            "content",
            "problem",
        )

        answer = self._first_value(
            data,
            "answer",
            "student_answer",
            "studentAnswer",
            "response",
        )

        correct = self._first_value(
            data,
            "correct",
            "is_correct",
            "isCorrect",
            "result",
        )

        concept_ids = self._first_value(
            data,
            "concept_ids",
            "conceptIds",
            "concepts",
        )

        timestamp = self._parse_timestamp(
            self._first_value(
                data,
                "timestamp",
                "created_at",
                "createdAt",
                "time",
                "datetime",
            )
        )

        normalized_concept_ids = (
            self._normalize_concept_ids(
                concept_ids,
            )
        )

        metadata = self._build_metadata(
            data=data,
            source=source,
        )

        if (
            question_id is None
            and question is None
            and answer is None
            and correct is None
            and not normalized_concept_ids
        ):
            return None

        return LearningInteraction(
            learner_id=learner_id,
            question_id=(
                str(question_id)
                if question_id is not None
                else None
            ),
            question=(
                str(question)
                if question is not None
                else ""
            ),
            answer=(
                str(answer)
                if answer is not None
                else ""
            ),
            correct=self._normalize_correctness(
                correct,
            ),
            concept_ids=normalized_concept_ids,
            timestamp=timestamp,
            metadata=metadata,
        )

    # ======================================================
    # Metadata
    # ======================================================

    @classmethod
    def _build_metadata(
        cls,
        data: dict[str, Any],
        source: str,
    ) -> dict[str, Any]:

        metadata: dict[str, Any] = {}

        for key in cls._METADATA_FIELDS:

            if key not in data:
                continue

            if key in cls._GOLD_FIELDS:
                continue

            value = data[key]

            if value is not None:
                metadata[key] = value

        metadata["evidence_source"] = source

        return metadata

    # ======================================================
    # Record normalization
    # ======================================================

    @staticmethod
    def _normalize_record(
        record: Any,
    ) -> dict[str, Any]:

        if record is None:
            return {}

        if isinstance(
            record,
            dict,
        ):
            return dict(record)

        if isinstance(
            record,
            str,
        ):
            return {
                "question": record,
            }

        if hasattr(
            record,
            "model_dump",
        ):
            try:
                value = record.model_dump()

                if isinstance(
                    value,
                    dict,
                ):
                    return value

            except Exception:
                pass

        if hasattr(
            record,
            "__dict__",
        ):
            try:
                value = vars(record)

                if isinstance(
                    value,
                    dict,
                ):
                    return dict(value)

            except Exception:
                pass

        return {}

    @staticmethod
    def _first_value(
        data: dict[str, Any],
        *keys: str,
    ) -> Any:

        for key in keys:

            if (
                key in data
                and data[key] is not None
            ):
                return data[key]

        return None

    @staticmethod
    def _normalize_concept_ids(
        value: Any,
    ) -> list[str]:

        if value is None:
            return []

        if isinstance(
            value,
            str,
        ):
            return [
                item.strip()
                for item in value.split(",")
                if item.strip()
            ]

        if isinstance(
            value,
            (list, tuple, set),
        ):
            return [
                str(item)
                for item in value
                if item is not None
            ]

        return [
            str(value)
        ]

    # ======================================================
    # Timestamp
    # ======================================================

    @staticmethod
    def _parse_timestamp(
        value: Any,
    ) -> datetime:

        if isinstance(
            value,
            datetime,
        ):

            if value.tzinfo is None:
                return value.replace(
                    tzinfo=UTC,
                )

            return value.astimezone(
                UTC,
            )

        if isinstance(
            value,
            (int, float),
        ):

            try:
                return datetime.fromtimestamp(
                    value,
                    tz=UTC,
                )

            except (
                OverflowError,
                OSError,
                ValueError,
            ):
                pass

        if isinstance(
            value,
            str,
        ):

            normalized = value.strip()

            if normalized:

                try:
                    parsed = datetime.fromisoformat(
                        normalized.replace(
                            "Z",
                            "+00:00",
                        )
                    )

                    if parsed.tzinfo is None:
                        parsed = parsed.replace(
                            tzinfo=UTC,
                        )

                    return parsed.astimezone(
                        UTC,
                    )

                except ValueError:
                    pass

        return datetime.fromtimestamp(
            0,
            tz=UTC,
        )

    # ======================================================
    # Correctness
    # ======================================================

    @staticmethod
    def _normalize_correctness(
        value: Any,
    ) -> bool | None:

        if value is None:
            return None

        if isinstance(
            value,
            bool,
        ):
            return value

        if isinstance(
            value,
            (int, float),
        ):
            return bool(value)

        if isinstance(
            value,
            str,
        ):

            normalized = value.strip().lower()

            if normalized in {
                "true",
                "correct",
                "right",
                "1",
                "yes",
                "success",
                "accepted",
            }:
                return True

            if normalized in {
                "false",
                "incorrect",
                "wrong",
                "0",
                "no",
                "fail",
                "failed",
                "rejected",
            }:
                return False

        return None