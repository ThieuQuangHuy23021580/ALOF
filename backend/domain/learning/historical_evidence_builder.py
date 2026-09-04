
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

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
    Build canonical historical evidence for ALOF.

    Responsibilities
    ----------------
    - Preserve native LearningState interactions.
    - Normalize external history into LearningInteraction.
    - Keep history_info and related_history semantically separate.
    - Preserve evidence fields required for downstream retrieval/reasoning.
    - Keep timestamp/correctness normalization deterministic.
    - Prevent benchmark Gold annotations from entering ALOF evidence.

    This component does NOT:
    - perform diagnosis;
    - rank evidence;
    - call an LLM;
    - access Gold answers.
    """

    _GOLD_FIELDS = {
        "gold_memory_queries",
        "gold_answer",
        "gold_answers",
    }

    _METADATA_FIELDS = {
        # Benchmark / dataset identity
        "_key",
        "record_id",
        "event_id",

        # Original evidence identifiers
        "question_id",
        "questionId",
        "qid",
        "id",

        # Question
        "question",
        "question_text",
        "questionText",
        "content",
        "problem",

        # Student response
        "answer",
        "student_answer",
        "studentAnswer",
        "response",

        # Correctness
        "correct",
        "is_correct",
        "isCorrect",
        "result",

        # Concepts
        "concept_ids",
        "conceptIds",
        "concepts",

        # Time
        "timestamp",
        "created_at",
        "createdAt",
        "time",
        "datetime",

        # Useful benchmark evidence metadata
        "source",
        "evidence_source",
        "history_source",
        "related",
        "related_history",
    }

    def __init__(
        self,
        recent_limit: int = 5,
    ) -> None:
        if recent_limit <= 0:
            raise ValueError(
                "recent_limit must be greater than 0."
            )

        self._recent_limit = recent_limit

    def build(
        self,
        learning_state: LearningState,
        current_question: str = "",
        related_concept_ids: list[str] | None = None,
        history_info: list[Any] | None = None,
        related_history: list[Any] | None = None,
    ) -> HistoricalEvidence:
        """
        Build historical evidence for the current task.

        Evidence sources
        ----------------
        1. LearningState.interactions
        2. External history_info
        3. External related_history

        External evidence is normalized into the canonical
        LearningInteraction representation.

        related_history remains separate from relevant_interactions.
        """

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
        # Recent native evidence
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
                    concept_id,
                )

        # ==================================================
        # Relevant native evidence
        # ==================================================

        if relevant_concepts:
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
                            concept_id,
                        )

        # ==================================================
        # External relevant history
        # ==================================================

        external_history_count = 0

        for record in history_info or []:
            interaction = self._to_learning_interaction(
                record=record,
                learner_id=learning_state.learner_id,
                source="history_info",
            )

            if interaction is None:
                continue

            evidence.add_relevant_interaction(
                interaction,
            )

            external_history_count += 1

            for concept_id in interaction.concept_ids:
                evidence.add_related_concept(
                    concept_id,
                )

        # ==================================================
        # External related history
        # ==================================================

        external_related_history_count = 0

        for record in related_history or []:
            interaction = self._to_learning_interaction(
                record=record,
                learner_id=learning_state.learner_id,
                source="related_history",
            )

            if interaction is None:
                continue

            evidence.add_related_interaction(
                interaction,
            )

            external_related_history_count += 1

            for concept_id in interaction.concept_ids:
                evidence.add_related_concept(
                    concept_id,
                )

        # ==================================================
        # Metadata
        # ==================================================

        evidence.set_metadata(
            "selection_strategy",
            "recent_and_relevant_with_related_external_history",
        )

        evidence.set_metadata(
            "recent_limit",
            self._recent_limit,
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
            external_history_count,
        )

        evidence.set_metadata(
            "external_related_history_count",
            external_related_history_count,
        )

        evidence.set_metadata(
            "external_evidence_count",
            (
                external_history_count
                + external_related_history_count
            ),
        )

        return evidence

    # ======================================================
    # External history normalization
    # ======================================================

    def _to_learning_interaction(
        self,
        record: Any,
        learner_id: str,
        source: str,
    ) -> LearningInteraction | None:
        """
        Normalize one external record.

        Only evidence-bearing fields are preserved.
        Gold annotations are explicitly excluded.
        """

        data = self._normalize_record(record)

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

        # A record without any meaningful evidence should
        # not become a useless interaction.
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
        """
        Preserve only known evidence metadata.

        This intentionally uses a whitelist rather than
        copying the complete benchmark record.
        """

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

        if isinstance(record, dict):
            return dict(record)

        if isinstance(record, str):
            return {
                "question": record,
            }

        if hasattr(record, "model_dump"):
            try:
                value = record.model_dump()

                if isinstance(value, dict):
                    return value

            except Exception:
                pass

        if hasattr(record, "__dict__"):
            try:
                value = vars(record)

                if isinstance(value, dict):
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

        if isinstance(value, str):
            return [
                item.strip()
                for item in value.split(",")
                if item.strip()
            ]

        if isinstance(value, (list, tuple, set)):
            return [
                str(item)
                for item in value
                if item is not None
            ]

        return [str(value)]

    # ======================================================
    # Timestamp
    # ======================================================

    @staticmethod
    def _parse_timestamp(
        value: Any,
    ) -> datetime:
        """
        Normalize timestamps to timezone-aware UTC.

        Missing/invalid timestamps use the Unix epoch rather
        than datetime.now(), so historical ordering remains
        deterministic.
        """

        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(
                    tzinfo=UTC,
                )

            return value.astimezone(UTC)

        if isinstance(value, (int, float)):
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

        if isinstance(value, str):
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

                    return parsed.astimezone(UTC)

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

        if isinstance(value, bool):
            return value

        if isinstance(value, (int, float)):
            return bool(value)

        if isinstance(value, str):
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

