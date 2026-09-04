
from __future__ import annotations

from typing import Any, Literal

from backend.application.runtime.evidence_selector import (
    EvidenceSelector,
)
from backend.domain.learning.historical_evidence_builder import (
    HistoricalEvidenceBuilder,
)
from backend.domain.learning.learning_state import LearningState


MemoryRetrievalMode = Literal[
    "context",
    "all",
]


class MemoryQueryService:
    """
    Retrieves historical evidence for memory queries.

    Retrieval modes
    ---------------
    context:
        Deterministic Top-K retrieval for contextual memory.

    all:
        Returns the complete canonical historical evidence set.
        This mode is required for aggregation/filtering questions
        such as count, date-based filtering, or exact-record lookup.

    This service:
    - receives QUERY ONLY;
    - never reads Gold answers;
    - never generates answers;
    - never performs benchmark-specific answer matching.
    """

    TOP_K = 5
    MAX_TOKENS = 1200

    def __init__(
        self,
        evidence_builder: HistoricalEvidenceBuilder | None = None,
    ) -> None:
        self._evidence_builder = (
            evidence_builder
            if evidence_builder is not None
            else HistoricalEvidenceBuilder()
        )

    def retrieve(
        self,
        learning_state: LearningState,
        query: str,
        history_info: list[Any] | None = None,
        related_history: list[Any] | None = None,
        mode: MemoryRetrievalMode = "context",
    ) -> dict[str, Any]:
        """
        Retrieve historical evidence for one memory query.

        Parameters
        ----------
        learning_state:
            Current learner state.

        query:
            Memory query only.

        history_info:
            Historical interaction records.

        related_history:
            Related historical interaction records.

        mode:
            - "context": deterministic Top-K selection.
            - "all": return all canonical evidence.
        """

        query = str(query or "").strip()

        if mode not in {"context", "all"}:
            raise ValueError(
                f"Unsupported memory retrieval mode: {mode!r}"
            )

        if not query:
            return {
                "query": "",
                "mode": mode,
                "history": [],
                "related_history": [],
                "stats": {},
            }

        evidence = self._evidence_builder.build(
            learning_state=learning_state,
            current_question=query,
            related_concept_ids=[],
            history_info=history_info or [],
            related_history=related_history or [],
        )

        if mode == "all":
            return self._retrieve_all(
                query=query,
                evidence=evidence,
            )

        return self._retrieve_context(
            query=query,
            evidence=evidence,
        )

    @staticmethod
    def infer_mode(
        query: str,
    ) -> MemoryRetrievalMode:
        """
        Infer the minimum retrieval scope required by a
        memory query.

        This does not answer the query.

        Queries involving counting, totals, or aggregation
        require the complete evidence set.
        """

        query = str(query or "").strip().lower()

        aggregation_markers = (
            # Chinese
            "多少",
            "几道",
            "几题",
            "共",
            "一共",
            "总数",
            "统计",
            "多少道",
            "多少题",
            "有几",
            "答对了几",
            "完成了多少",
            "尝试了多少",

            # English
            "how many",
            "number of",
            "total",
            "count",
            "how much",
        )

        if any(
            marker in query
            for marker in aggregation_markers
        ):
            return "all"

        return "context"

    def _retrieve_context(
        self,
        query: str,
        evidence: Any,
    ) -> dict[str, Any]:
        """
        Retrieve a bounded contextual memory set.
        """

        selection = EvidenceSelector.select(
            current_question=query,
            current_concept_ids=[],
            interactions=(
                list(evidence.relevant_interactions)
                + list(evidence.recent_interactions)
            ),
            related_history=list(
                evidence.related_interactions
            ),
            top_k=self.TOP_K,
            max_tokens=self.MAX_TOKENS,
        )

        stats = dict(
            selection.get(
                "stats",
                {},
            )
        )

        stats["retrieval_mode"] = "context"

        return {
            "query": query,
            "mode": "context",
            "history": self._serialize_interactions(
                selection["history"]
            ),
            "related_history": self._serialize_interactions(
                selection["related_history"]
            ),
            "stats": self._json_safe(stats),
        }

    @staticmethod
    def _retrieve_all(
        query: str,
        evidence: Any,
    ) -> dict[str, Any]:
        """
        Return the complete canonical evidence set.

        No Top-K truncation is applied because aggregation,
        filtering, and exact historical lookup may require
        records outside the contextual Top-K window.
        """

        history = (
            list(evidence.relevant_interactions)
            + list(evidence.recent_interactions)
        )

        related_history = list(
            evidence.related_interactions
        )

        stats = {
            "retrieval_mode": "all",
            "history_candidates": len(history),
            "related_history_candidates": len(
                related_history
            ),
            "selected_count": (
                len(history)
                + len(related_history)
            ),
        }

        return {
            "query": query,
            "mode": "all",
            "history": MemoryQueryService._serialize_interactions(
                history
            ),
            "related_history": MemoryQueryService._serialize_interactions(
                related_history
            ),
            "stats": MemoryQueryService._json_safe(
                stats
            ),
        }

    @staticmethod
    def _json_safe(
        value: Any,
    ) -> Any:
        """
        Convert arbitrary nested values into JSON-safe values.

        Handles:
        - Pydantic models;
        - datetime/date-like objects;
        - dictionaries;
        - lists/tuples;
        - nested combinations of the above.
        """

        if hasattr(
            value,
            "model_dump",
        ):
            return MemoryQueryService._json_safe(
                value.model_dump()
            )

        if isinstance(
            value,
            dict,
        ):
            return {
                str(key): MemoryQueryService._json_safe(
                    item
                )
                for key, item in value.items()
            }

        if isinstance(
            value,
            (list, tuple),
        ):
            return [
                MemoryQueryService._json_safe(
                    item
                )
                for item in value
            ]

        if hasattr(
            value,
            "isoformat",
        ):
            return value.isoformat()

        return value

    @staticmethod
    def _serialize_interactions(
        items: list[Any],
    ) -> list[dict[str, Any]]:
        """
        Convert canonical LearningInteraction objects
        into JSON-safe dictionaries.
        """

        result: list[dict[str, Any]] = []

        for item in items:
            serialized = MemoryQueryService._json_safe(
                item
            )

            if isinstance(
                serialized,
                dict,
            ):
                result.append(
                    serialized
                )

        return result

