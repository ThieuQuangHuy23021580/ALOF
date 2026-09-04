
from __future__ import annotations

import json
import re
from typing import Any


class EvidenceSelector:
    """
    Deterministic selector for learner historical evidence.

    Responsibilities
    ----------------
    - Select evidence relevant to the current learning task.
    - Rank evidence using deterministic learning signals.
    - Support native ALOF interactions and benchmark history.
    - Enforce top-k and token-budget constraints.
    - Deduplicate historical evidence.
    - Produce optional diagnostic retrieval traces.
    - Never call an LLM.
    - Never access Gold benchmark annotations.

    This class belongs to the runtime/application layer.
    It decides WHICH evidence should be exposed to a component.

    It does not:
    - perform diagnosis;
    - generate answers;
    - access Gold answers;
    - call an LLM;
    - build prompts.
    """

    DEFAULT_TOP_K = 5
    DEFAULT_MAX_TOKENS = 1200

    # Maximum serialized size of a single evidence record.
    MAX_RECORD_CHARS = 1800

    # Maximum number of candidates exposed through diagnostics.
    DEBUG_MAX_CANDIDATES = 20

    _STOPWORDS = {
        # Chinese
        "学生",
        "回答",
        "题目",
        "问题",
        "关于",
        "什么",
        "哪个",
        "哪些",
        "是否",
        "请问",
        "具体",
        "内容",
        "情况",
        "这道",
        "题",
        "的",
        "了",
        "是",
        "在",
        "和",
        "与",
        "有",
        "中",
        "为",
        "对",
        "进行",
        "一个",
        "一共",
        "多少",
        "时候",
        "当天",
        "这一天",
        "正确",
        "错误",
        "学生在",
        # English
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "of",
        "to",
        "in",
        "on",
        "and",
        "or",
        "for",
        "with",
        "what",
        "which",
        "how",
        "many",
        "did",
        "does",
        "student",
        "question",
        "problem",
    }

    # ==========================================================
    # Public API
    # ==========================================================

    @classmethod
    def select(
        cls,
        *,
        current_question: str,
        current_concept_ids: list[str] | None = None,
        interactions: list[Any] | None = None,
        related_history: list[Any] | None = None,
        top_k: int = DEFAULT_TOP_K,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> dict[str, Any]:
        """
        Select the most relevant historical evidence.

        Returns
        -------
        {
            "history": [...],
            "related_history": [...],
            "stats": {...},
        }

        The returned ``stats`` now also contains deterministic
        diagnostic information describing candidate ranking and
        selected evidence.

        Diagnostic information contains only evidence-derived
        metadata. Gold annotations are never consulted.
        """

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than 0."
            )

        if max_tokens <= 0:
            raise ValueError(
                "max_tokens must be greater than 0."
            )

        question = str(
            current_question or ""
        ).strip()

        concept_ids = {
            str(value).strip().lower()
            for value in (current_concept_ids or [])
            if value is not None
            and str(value).strip()
        }

        history = cls._normalize_records(
            interactions or []
        )

        related = cls._normalize_records(
            related_history or []
        )

        history_candidates = cls._build_candidates(
            records=history,
            source="history",
            current_question=question,
            current_concept_ids=concept_ids,
        )

        related_candidates = cls._build_candidates(
            records=related,
            source="related_history",
            current_question=question,
            current_concept_ids=concept_ids,
        )

        candidates = (
            history_candidates
            + related_candidates
        )

        candidates.sort(
            key=lambda candidate: (
                -float(candidate["score"]),
                -int(candidate["recency_rank"]),
                int(candidate["original_index"]),
            )
        )

        selected: list[dict[str, Any]] = []
        selected_keys: set[str] = set()

        estimated_tokens_before = cls._estimate_tokens(
            [
                candidate["record"]
                for candidate in candidates
            ]
        )

        used_tokens = 0

        for candidate in candidates:

            if len(selected) >= top_k:
                break

            record = candidate["record"]

            dedupe_key = cls._dedupe_key(
                record
            )

            if dedupe_key in selected_keys:
                continue

            token_cost = cls._estimate_tokens(
                [record]
            )

            if token_cost <= 0:
                continue

            if used_tokens + token_cost > max_tokens:
                continue

            selected.append(
                candidate
            )

            selected_keys.add(
                dedupe_key
            )

            used_tokens += token_cost

        selected_history = [
            candidate["record"]
            for candidate in selected
            if candidate["source"] == "history"
        ]

        selected_related_history = [
            candidate["record"]
            for candidate in selected
            if candidate["source"]
            == "related_history"
        ]

        estimated_tokens_after = cls._estimate_tokens(
            selected
        )

        return {
            "history": selected_history,
            "related_history": selected_related_history,
            "stats": {
                "history_candidates": len(history),
                "related_history_candidates": len(related),
                "total_candidates": len(candidates),
                "selected_count": len(selected),
                "selected_history_count": len(
                    selected_history
                ),
                "selected_related_history_count": len(
                    selected_related_history
                ),
                "estimated_tokens_before": (
                    estimated_tokens_before
                ),
                "estimated_tokens_after": (
                    estimated_tokens_after
                ),
                "token_reduction": max(
                    0,
                    estimated_tokens_before
                    - estimated_tokens_after,
                ),
                "top_k": top_k,
                "max_tokens": max_tokens,

                # ==================================================
                # Diagnostic retrieval trace
                # ==================================================
                "debug": {
                    "query": question,
                    "concept_ids": sorted(
                        concept_ids
                    ),
                    "candidate_rankings": [
                        cls._diagnostic_candidate(
                            candidate
                        )
                        for candidate in candidates[
                            : cls.DEBUG_MAX_CANDIDATES
                        ]
                    ],
                    "selected": [
                        cls._diagnostic_candidate(
                            candidate
                        )
                        for candidate in selected
                    ],
                },
            },
        }

    # ==========================================================
    # Candidate construction
    # ==========================================================

    @classmethod
    def _build_candidates(
        cls,
        *,
        records: list[dict[str, Any]],
        source: str,
        current_question: str,
        current_concept_ids: set[str],
    ) -> list[dict[str, Any]]:

        candidates: list[dict[str, Any]] = []

        total_count = len(records)

        for index, record in enumerate(records):

            score_data = cls._score_record(
                record=record,
                current_question=current_question,
                current_concept_ids=current_concept_ids,
                original_index=index,
                total_count=total_count,
            )

            if source == "related_history":
                score_data["score"] += 1.0
                score_data["selection_reasons"].append(
                    "related_history"
                )

            candidates.append(
                {
                    **score_data,
                    "source": source,
                }
            )

        return candidates

    # ==========================================================
    # Scoring
    # ==========================================================

    @classmethod
    def _score_record(
        cls,
        *,
        record: dict[str, Any],
        current_question: str,
        current_concept_ids: set[str],
        original_index: int,
        total_count: int,
    ) -> dict[str, Any]:

        record_concepts = {
            value.lower()
            for value in cls._extract_concepts(
                record
            )
        }

        concept_overlap = (
            current_concept_ids
            & record_concepts
        )

        question_ids = cls._extract_question_ids(
            current_question
        )

        record_ids = cls._extract_question_ids(
            cls._record_text(record)
        )

        question_id_overlap = (
            set(question_ids)
            & set(record_ids)
        )

        date_overlap = cls._date_overlap(
            current_question,
            cls._record_text(record),
        )

        lexical_overlap = cls._lexical_overlap(
            current_question,
            cls._record_text(record),
        )

        correctness_score = cls._correctness_score(
            record
        )

        recency_rank = (
            original_index
            if total_count > 0
            else 0
        )

        recency_score = (
            (original_index + 1)
            / max(total_count, 1)
        )

        score = (
            len(question_id_overlap) * 20.0
            + len(concept_overlap) * 8.0
            + date_overlap * 5.0
            + lexical_overlap * 5.0
            + correctness_score
            + recency_score * 2.0
        )

        reasons: list[str] = []

        if question_id_overlap:
            reasons.append(
                "question_id_match"
            )

        if concept_overlap:
            reasons.append(
                "concept_match"
            )

        if date_overlap > 0:
            reasons.append(
                "date_match"
            )

        if lexical_overlap > 0:
            reasons.append(
                "question_overlap"
            )

        if correctness_score > 0:
            reasons.append(
                "learning_signal"
            )

        if recency_score > 0.5:
            reasons.append(
                "recent"
            )

        return {
            "record": cls._compact_record(
                record
            ),
            "score": score,
            "recency_rank": recency_rank,
            "original_index": original_index,
            "selection_reasons": reasons,
            "question_id_overlap": sorted(
                question_id_overlap
            ),
            "concept_overlap": sorted(
                concept_overlap
            ),
            "date_overlap": date_overlap,
            "lexical_overlap": lexical_overlap,
        }

    # ==========================================================
    # Diagnostic serialization
    # ==========================================================

    @staticmethod
    def _diagnostic_candidate(
        candidate: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Serialize ranking information for diagnostics.

        This intentionally excludes Gold annotations and does
        not expose the internal candidate object itself.
        """

        record = candidate["record"]

        return {
            "source": candidate["source"],
            "score": round(
                float(candidate["score"]),
                4,
            ),
            "original_index": candidate[
                "original_index"
            ],
            "recency_rank": candidate[
                "recency_rank"
            ],
            "selection_reasons": list(
                candidate[
                    "selection_reasons"
                ]
            ),
            "question_id_overlap": list(
                candidate[
                    "question_id_overlap"
                ]
            ),
            "concept_overlap": list(
                candidate[
                    "concept_overlap"
                ]
            ),
            "date_overlap": round(
                float(candidate["date_overlap"]),
                4,
            ),
            "lexical_overlap": round(
                float(candidate["lexical_overlap"]),
                4,
            ),
            "question_id": record.get(
                "question_id",
                record.get("id"),
            ),
            "question": record.get(
                "question",
                record.get("query", ""),
            ),
            "answer": record.get(
                "answer",
                "",
            ),
            "correct": record.get(
                "correct",
            ),
            "timestamp": record.get(
                "timestamp",
            ),
        }

    # ==========================================================
    # Normalization
    # ==========================================================

    @classmethod
    def _normalize_records(
        cls,
        records: list[Any],
    ) -> list[dict[str, Any]]:

        normalized: list[dict[str, Any]] = []

        for item in records:

            record = cls._normalize_record(
                item
            )

            if not record:
                continue

            if not cls._has_content(record):
                continue

            normalized.append(record)

        return normalized

    @classmethod
    def _normalize_record(
        cls,
        item: Any,
    ) -> dict[str, Any]:

        if isinstance(item, dict):
            return dict(item)

        if isinstance(item, str):

            text = item.strip()

            if not text:
                return {}

            parsed = cls._try_parse_json(
                text
            )

            if isinstance(parsed, dict):
                return parsed

            return {
                "question": text,
                "answer": "",
            }

        if hasattr(item, "model_dump"):

            try:
                value = item.model_dump()

                if isinstance(value, dict):
                    return value

            except Exception:
                pass

        if hasattr(item, "__dict__"):

            try:
                value = dict(vars(item))

                if value:
                    return value

            except Exception:
                pass

        return {}

    @staticmethod
    def _try_parse_json(
        text: str,
    ) -> Any:

        try:
            return json.loads(text)

        except Exception:
            return None

    @staticmethod
    def _has_content(
        record: dict[str, Any],
    ) -> bool:

        fields = (
            "question",
            "query",
            "answer",
            "concept",
            "concept_ids",
            "question_id",
            "id",
            "timestamp",
            "result",
            "correct",
        )

        return any(
            record.get(field) is not None
            and str(record.get(field)).strip()
            for field in fields
        )

    # ==========================================================
    # Concept extraction
    # ==========================================================

    @classmethod
    def _extract_concepts(
        cls,
        record: dict[str, Any],
    ) -> list[str]:

        values: list[str] = []

        concept_ids = record.get(
            "concept_ids"
        )

        if isinstance(
            concept_ids,
            (list, tuple, set),
        ):

            values.extend(
                str(value).strip()
                for value in concept_ids
                if value is not None
                and str(value).strip()
            )

        elif concept_ids is not None:

            values.append(
                str(concept_ids).strip()
            )

        concept = record.get(
            "concept"
        )

        if isinstance(
            concept,
            (list, tuple, set),
        ):

            values.extend(
                str(value).strip()
                for value in concept
                if value is not None
                and str(value).strip()
            )

        elif concept is not None:

            values.append(
                str(concept).strip()
            )

        return list(
            dict.fromkeys(
                value
                for value in values
                if value
            )
        )

    # ==========================================================
    # Question identifiers
    # ==========================================================

    @staticmethod
    def _extract_question_ids(
        text: str,
    ) -> list[str]:

        if not text:
            return []

        patterns = (
            r"(?:题目|问题|记录|ID|id)"
            r"\s*[\[\(]?\s*(\d+)\s*[\]\)]?",
            r"\bquestion[_\s-]*id"
            r"\s*[:=]?\s*(\d+)",
            r"\bproblem[_\s-]*id"
            r"\s*[:=]?\s*(\d+)",
        )

        values: list[str] = []

        for pattern in patterns:

            values.extend(
                re.findall(
                    pattern,
                    text,
                    flags=re.IGNORECASE,
                )
            )

        return list(
            dict.fromkeys(values)
        )

    # ==========================================================
    # Date relevance
    # ==========================================================

    @classmethod
    def _date_overlap(
        cls,
        question: str,
        record_text: str,
    ) -> float:

        question_dates = cls._extract_dates(
            question
        )

        if not question_dates:
            return 0.0

        record_dates = cls._extract_dates(
            record_text
        )

        if not record_dates:
            return 0.0

        overlap = (
            question_dates
            & record_dates
        )

        if not overlap:
            return 0.0

        return min(
            1.0,
            len(overlap)
            / max(
                len(question_dates),
                1,
            ),
        )

    @staticmethod
    def _extract_dates(
        text: str,
    ) -> set[str]:

        if not text:
            return set()

        matches = re.findall(
            r"""
            (20\d{2})
            [-/年]
            (\d{1,2})
            [-/月]
            (\d{1,2})
            (?:日)?
            """,
            text,
            flags=re.VERBOSE,
        )

        return {
            f"{year}-{int(month):02d}-{int(day):02d}"
            for year, month, day in matches
        }

    # ==========================================================
    # Lexical relevance
    # ==========================================================

    @classmethod
    def _lexical_overlap(
        cls,
        query: str,
        text: str,
    ) -> float:

        query_terms = cls._terms(
            query
        )

        text_terms = cls._terms(
            text
        )

        if not query_terms or not text_terms:
            return 0.0

        overlap = (
            query_terms
            & text_terms
        )

        return min(
            1.0,
            len(overlap)
            / max(
                len(query_terms),
                1,
            ),
        )

    @classmethod
    def _terms(
        cls,
        text: str,
    ) -> set[str]:

        if not text:
            return set()

        normalized = text.lower()

        terms: set[str] = set()

        for token in re.findall(
            r"[a-z0-9_]+",
            normalized,
        ):

            if (
                token
                and token not in cls._STOPWORDS
            ):
                terms.add(token)

        sequences = re.findall(
            r"[\u4e00-\u9fff]+",
            normalized,
        )

        for sequence in sequences:

            if len(sequence) == 1:

                if sequence not in cls._STOPWORDS:
                    terms.add(sequence)

                continue

            for index in range(
                len(sequence) - 1
            ):

                gram = sequence[
                    index:index + 2
                ]

                if gram not in cls._STOPWORDS:
                    terms.add(gram)

        return terms

    # ==========================================================
    # Learning signal
    # ==========================================================

    @staticmethod
    def _correctness_score(
        record: dict[str, Any],
    ) -> float:

        correct = record.get(
            "correct"
        )

        if correct is True:
            return 1.0

        if correct is False:
            return 2.0

        result = record.get(
            "result"
        )

        if result is None:
            return 0.0

        normalized = str(
            result
        ).strip().lower()

        if normalized in {
            "wrong",
            "incorrect",
            "false",
            "error",
            "错误",
        }:
            return 2.0

        if normalized in {
            "correct",
            "true",
            "right",
            "正确",
        }:
            return 1.0

        return 0.0

    # ==========================================================
    # Record text
    # ==========================================================

    @staticmethod
    def _record_text(
        record: dict[str, Any],
    ) -> str:

        parts: list[str] = []

        for key in (
            "question",
            "query",
            "answer",
            "concept",
            "concept_ids",
            "question_id",
            "id",
            "timestamp",
            "result",
            "correct",
        ):

            value = record.get(
                key
            )

            if value is None:
                continue

            if isinstance(
                value,
                (list, tuple, set),
            ):

                parts.extend(
                    str(item)
                    for item in value
                )

            else:

                parts.append(
                    str(value)
                )

        return " ".join(parts)

    # ==========================================================
    # Compact evidence
    # ==========================================================

    @classmethod
    def _compact_record(
        cls,
        record: dict[str, Any],
    ) -> dict[str, Any]:

        preferred_fields = (
            "question_id",
            "id",
            "question",
            "query",
            "answer",
            "concept",
            "concept_ids",
            "timestamp",
            "result",
            "correct",
            "thinking_time",
        )

        compact: dict[str, Any] = {}

        for field in preferred_fields:

            if field not in record:
                continue

            value = record[field]

            if value is None:
                continue

            compact[field] = value

        if not compact:
            compact = dict(record)

        return cls._truncate_record(
            compact
        )

    @classmethod
    def _truncate_record(
        cls,
        record: dict[str, Any],
    ) -> dict[str, Any]:

        serialized = json.dumps(
            record,
            ensure_ascii=False,
            default=str,
        )

        if len(serialized) <= cls.MAX_RECORD_CHARS:
            return record

        compact = dict(record)

        for field in (
            "answer",
            "question",
            "query",
        ):

            value = compact.get(
                field
            )

            if not isinstance(
                value,
                str,
            ):
                continue

            compact[field] = value[
                :600
            ]

            serialized = json.dumps(
                compact,
                ensure_ascii=False,
                default=str,
            )

            if len(serialized) <= cls.MAX_RECORD_CHARS:
                break

        return compact

    # ==========================================================
    # Deduplication
    # ==========================================================

    @classmethod
    def _dedupe_key(
        cls,
        record: dict[str, Any],
    ) -> str:

        for field in (
            "question_id",
            "id",
        ):

            value = record.get(
                field
            )

            if value is not None:

                text = str(
                    value
                ).strip()

                if text:
                    return (
                        f"{field}:{text}"
                    )

        identity_fields = (
            "question",
            "query",
            "timestamp",
            "concept",
        )

        values = [
            str(record.get(field, "")).strip()
            for field in identity_fields
        ]

        return "|".join(values)

    # ==========================================================
    # Token estimation
    # ==========================================================

    @staticmethod
    def _estimate_tokens(
        records: list[Any],
    ) -> int:

        if not records:
            return 0

        text = json.dumps(
            records,
            ensure_ascii=False,
            default=str,
        )

        try:
            import tiktoken

            encoding = tiktoken.get_encoding(
                "cl100k_base"
            )

            return len(
                encoding.encode(text)
            )

        except Exception:

            return max(
                1,
                len(text) // 4,
            )
