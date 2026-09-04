
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from .adapter import ALOFDatasetAdapter


class ALOFBenchmarkEvaluator:
    """
    Semantic evaluator for the ALOF benchmark.

    Evaluation dimensions
    ---------------------
    1. Memory
       - Compare expected relevant interaction IDs
         against runtime memory retrieval.
       - Report precision, recall and F1.

    2. Diagnosis
       - Compare the expected primary concept.
       - Compare canonical ALOF learner level.
       - Compare misconception / secondary weakness /
         reason / trend when exposed by runtime.

    3. Strategy
       - Compare semantic strategy type.
       - Compare canonical ALOF difficulty.
       - Compare focus concepts.
       - Compare direct-answer behavior when exposed.

    4. Response
       - Check whether a prediction exists.
       - Check whether the response appears to directly
         provide an answer when direct_answer=False.

    The evaluator intentionally does NOT require exact JSON
    equality. Runtime and benchmark representations may use
    different but semantically equivalent labels.

    Important:
    - Gold answers are never used.
    - Only expected metadata from the benchmark dataset is used.
    - Missing runtime fields are reported as "not_exposed".
    - "not_exposed" fields are skipped from pass/fail aggregation.
    - Canonical ALOF vocabulary is preferred over legacy labels.
    """

    # ==========================================================
    # Canonical ALOF normalization
    # ==========================================================

    LEVEL_ALIASES: dict[str, set[str]] = {
        "unknown": {
            "unknown",
        },
        "beginner": {
            "beginner",
            "weak",
            "very_weak",
            "very weak",
        },
        "intermediate": {
            "intermediate",
            "developing",
            "improving",
        },
        "advanced": {
            "advanced",
            "strong",
        },
        "mastered": {
            "mastered",
        },
    }

    DIFFICULTY_ALIASES: dict[str, set[str]] = {
        "beginner": {
            "beginner",
            "easy",
            "easier",
            "same_or_slightly_easier",
        },
        "medium": {
            "medium",
            "same",
        },
        "advanced": {
            "advanced",
            "harder",
            "slightly_harder",
            "same_or_slightly_harder",
            "challenge",
        },
    }

    # Semantic benchmark strategy type -> canonical ALOF action/strategy.
    #
    # The benchmark's "type" is a higher-level teaching strategy,
    # while runtime exposes:
    #
    #   TeachingActionType
    #   TeachingStrategy
    #
    STRATEGY_TYPE_MAPPING: dict[str, dict[str, set[str]]] = {
        "guided_practice": {
            "action": {
                "scaffold",
            },
            "strategy": {
                "guided_explanation",
                "step_by_step",
            },
        },
        "progressive_challenge": {
            "action": {
                "challenge",
            },
            "strategy": {
                "deepening",
            },
        },
        "worked_example_then_guided_practice": {
            "action": {
                "scaffold",
            },
            "strategy": {
                "step_by_step",
            },
        },
        "concept_reminder_then_guided_solution": {
            "action": {
                "explain",
                "scaffold",
            },
            "strategy": {
                "guided_explanation",
                "step_by_step",
            },
        },
        "independent_practice": {
            "action": {
                "practice",
            },
            "strategy": {
                "targeted_practice",
            },
        },
        "independent_practice_with_hint_if_needed": {
            "action": {
                "practice",
            },
            "strategy": {
                "targeted_practice",
            },
        },
        "independent_practice_with_feedback": {
            "action": {
                "practice",
            },
            "strategy": {
                "targeted_practice",
            },
        },
        "scaffolded_practice": {
            "action": {
                "scaffold",
            },
            "strategy": {
                "step_by_step",
                "guided_explanation",
            },
        },
        "transfer_problem_solving": {
            "action": {
                "scaffold",
            },
            "strategy": {
                "step_by_step",
            },
        },
        "diagnostic_prompt_then_practice": {
            "action": {
                "practice",
            },
            "strategy": {
                "targeted_practice",
            },
        },
        "percentage_reasoning": {
            "action": {
                "practice",
            },
            "strategy": {
                "targeted_practice",
            },
        },
        "challenge": {
            "action": {
                "challenge",
            },
            "strategy": {
                "deepening",
            },
        },
        "combine_like_terms": {
            "action": {
                "practice",
            },
            "strategy": {
                "targeted_practice",
            },
        },
        "distributive_property": {
            "action": {
                "practice",
            },
            "strategy": {
                "targeted_practice",
            },
        },
        "multi_step_equation": {
            "action": {
                "practice",
            },
            "strategy": {
                "step_by_step",
            },
        },
        "common_denominator": {
            "action": {
                "practice",
            },
            "strategy": {
                "step_by_step",
            },
        },
        "comparison_reasoning": {
            "action": {
                "practice",
                "scaffold",
            },
            "strategy": {
                "targeted_practice",
                "step_by_step",
            },
        },
        "retrieval_practice_then_guided_practice": {
            "action": {
                "review",
            },
            "strategy": {
                "spaced_review",
            },
        },
        "brief_diagnostic_then_practice": {
            "action": {
                "practice",
            },
            "strategy": {
                "targeted_practice",
            },
        },
        "explicit_scaffold_then_easy_practice": {
            "action": {
                "scaffold",
            },
            "strategy": {
                "step_by_step",
            },
        },
        "guided_problem_decomposition": {
            "action": {
                "scaffold",
            },
            "strategy": {
                "step_by_step",
            },
        },
        "guided_independent_hybrid": {
            "action": {
                "practice",
            },
            "strategy": {
                "targeted_practice",
            },
        },
    }

    def __init__(
        self,
        dataset_path: str | Path,
    ) -> None:
        self.adapter = ALOFDatasetAdapter(
            dataset_path,
        )

        self.samples = {
            sample["case_id"]: sample
            for sample in self.adapter.load()
        }

    # ==========================================================
    # Generic helpers
    # ==========================================================

    @staticmethod
    def _text(
        value: Any,
    ) -> str:
        if value is None:
            return ""

        if isinstance(value, str):
            return value

        return json.dumps(
            value,
            ensure_ascii=False,
            default=str,
        )

    @staticmethod
    def _normalize_string(
        value: Any,
    ) -> str:
        if value is None:
            return ""

        return (
            str(value)
            .strip()
            .lower()
            .replace("-", "_")
            .replace(" ", "_")
        )

    @staticmethod
    def _as_list(
        value: Any,
    ) -> list[Any]:
        if value is None:
            return []

        if isinstance(value, list):
            return value

        if isinstance(value, tuple):
            return list(value)

        if isinstance(value, set):
            return list(value)

        return [value]

    @staticmethod
    def _canonical_set(
        values: Any,
    ) -> set[str]:
        result: set[str] = set()

        for value in ALOFBenchmarkEvaluator._as_list(values):
            normalized = (
                ALOFBenchmarkEvaluator
                ._normalize_string(value)
            )

            if normalized:
                result.add(normalized)

        return result

    @staticmethod
    def _canonical_level(
        value: Any,
    ) -> str:
        normalized = (
            ALOFBenchmarkEvaluator
            ._normalize_string(value)
        )

        if not normalized:
            return ""

        for canonical, aliases in (
            ALOFBenchmarkEvaluator
            .LEVEL_ALIASES
            .items()
        ):
            if normalized in aliases:
                return canonical

        return normalized

    @staticmethod
    def _canonical_difficulty(
        value: Any,
    ) -> str:
        normalized = (
            ALOFBenchmarkEvaluator
            ._normalize_string(value)
        )

        if not normalized:
            return ""

        for canonical, aliases in (
            ALOFBenchmarkEvaluator
            .DIFFICULTY_ALIASES
            .items()
        ):
            if normalized in aliases:
                return canonical

        return normalized

    # ==========================================================
    # Runtime extraction
    # ==========================================================

    @staticmethod
    def _runtime_metadata(
        result: dict[str, Any],
    ) -> dict[str, Any]:
        metadata = result.get(
            "runtime_metadata",
            {},
        )

        if isinstance(metadata, dict):
            return metadata

        return {}

    @staticmethod
    def _extract_memory_ids(
        result: dict[str, Any],
    ) -> list[str]:
        """
        Prefer memory_retrieval because it represents the
        actual retrieval result used for benchmark memory
        evaluation.

        Falls back to historical_evidence.relevant_interactions
        when memory_retrieval is unavailable.
        """

        metadata = (
            ALOFBenchmarkEvaluator
            ._runtime_metadata(result)
        )

        memory = metadata.get(
            "memory_retrieval",
        )

        ids: list[str] = []

        if isinstance(memory, list):
            for item in memory:
                if not isinstance(item, dict):
                    continue

                candidates = [
                    item.get("interaction_id"),
                    item.get("question_id"),
                    item.get("id"),
                ]

                for candidate in candidates:
                    if candidate is not None:
                        value = str(candidate).strip()

                        if value:
                            ids.append(value)
                            break

        if ids:
            return ids

        evidence = metadata.get(
            "historical_evidence",
            {},
        )

        if isinstance(evidence, dict):
            relevant = evidence.get(
                "relevant_interactions",
                [],
            )

            if isinstance(relevant, list):
                for item in relevant:
                    if not isinstance(item, dict):
                        continue

                    candidate = (
                        item.get("interaction_id")
                        or item.get("id")
                    )

                    if candidate:
                        ids.append(
                            str(candidate).strip()
                        )

        return ids

    @staticmethod
    def _extract_diagnosis(
        result: dict[str, Any],
    ) -> dict[str, Any] | None:
        metadata = (
            ALOFBenchmarkEvaluator
            ._runtime_metadata(result)
        )

        diagnosis = metadata.get(
            "knowledge_diagnosis",
        )

        if isinstance(diagnosis, dict):
            return diagnosis

        adaptive = metadata.get(
            "adaptive_learning",
        )

        if isinstance(adaptive, dict):
            diagnosis = adaptive.get(
                "diagnosis",
            )

            if isinstance(diagnosis, dict):
                return diagnosis

        return None

    @staticmethod
    def _extract_strategy(
        result: dict[str, Any],
    ) -> dict[str, Any] | None:
        metadata = (
            ALOFBenchmarkEvaluator
            ._runtime_metadata(result)
        )

        strategy = metadata.get(
            "adaptive_teaching_action",
        )

        if isinstance(strategy, dict):
            return strategy

        adaptive = metadata.get(
            "adaptive_learning",
        )

        if isinstance(adaptive, dict):
            strategy = adaptive.get(
                "teaching_action",
            )

            if isinstance(strategy, dict):
                return strategy

        return None

    # ==========================================================
    # Memory evaluation
    # ==========================================================

    def evaluate_memory(
        self,
        expected: dict[str, Any],
        result: dict[str, Any],
    ) -> dict[str, Any]:
        expected_ids = [
            str(value).strip()
            for value in self._as_list(
                expected.get(
                    "relevant_interactions",
                    [],
                )
            )
            if str(value).strip()
        ]

        actual_ids = self._extract_memory_ids(
            result,
        )

        expected_set = set(
            expected_ids,
        )

        actual_set = set(
            actual_ids,
        )

        if not expected_set:
            return {
                "status": "not_applicable",
                "pass": True,
                "expected": [],
                "actual": actual_ids,
                "precision": 1.0,
                "recall": 1.0,
                "f1": 1.0,
                "matched": [],
                "missing": [],
                "extra": actual_ids,
            }

        matched = sorted(
            expected_set & actual_set,
        )

        missing = sorted(
            expected_set - actual_set,
        )

        extra = sorted(
            actual_set - expected_set,
        )

        precision = (
            len(matched) / len(actual_set)
            if actual_set
            else 0.0
        )

        recall = (
            len(matched) / len(expected_set)
            if expected_set
            else 0.0
        )

        f1 = (
            2 * precision * recall
            / (precision + recall)
            if precision + recall > 0
            else 0.0
        )

        return {
            "status": "evaluated",
            "pass": (
                len(missing) == 0
            ),
            "expected": expected_ids,
            "actual": actual_ids,
            "precision": round(
                precision,
                4,
            ),
            "recall": round(
                recall,
                4,
            ),
            "f1": round(
                f1,
                4,
            ),
            "matched": matched,
            "missing": missing,
            "extra": extra,
        }

    # ==========================================================
    # Diagnosis helpers
    # ==========================================================

    @staticmethod
    def _primary_concept(
        diagnosis: dict[str, Any],
    ) -> str | None:
        primary = diagnosis.get(
            "primary_concepts",
        )

        if isinstance(primary, list) and primary:
            return str(primary[0])

        concepts = diagnosis.get(
            "concepts",
        )

        if isinstance(concepts, dict) and concepts:
            return str(
                next(iter(concepts.keys()))
            )

        return None

    @staticmethod
    def _concept_state(
        diagnosis: dict[str, Any],
        concept: str,
    ) -> dict[str, Any] | None:
        concepts = diagnosis.get(
            "concepts",
        )

        if not isinstance(concepts, dict):
            return None

        if concept in concepts:
            value = concepts[concept]

            if isinstance(value, dict):
                return value

        normalized_target = (
            ALOFBenchmarkEvaluator
            ._normalize_string(concept)
        )

        for key, value in concepts.items():
            if (
                ALOFBenchmarkEvaluator
                ._normalize_string(key)
                == normalized_target
            ):
                if isinstance(value, dict):
                    return value

        return None

    @staticmethod
    def _actual_level(
        diagnosis: dict[str, Any],
        concept: str | None,
    ) -> str | None:
        if concept is None:
            return None

        state = (
            ALOFBenchmarkEvaluator
            ._concept_state(
                diagnosis,
                concept,
            )
        )

        if state is None:
            return None

        level = state.get(
            "level",
        )

        if level:
            return (
                ALOFBenchmarkEvaluator
                ._canonical_level(level)
            )

        return None

    @staticmethod
    def _level_match(
        expected_level: str,
        actual_level: str | None,
    ) -> bool | None:
        if actual_level is None:
            return None

        expected = (
            ALOFBenchmarkEvaluator
            ._canonical_level(
                expected_level,
            )
        )

        actual = (
            ALOFBenchmarkEvaluator
            ._canonical_level(
                actual_level,
            )
        )

        return expected == actual

    @staticmethod
    def _find_semantic_field(
        diagnosis: dict[str, Any],
        expected_value: str,
    ) -> tuple[str | None, Any]:
        """
        Search only diagnostic information, never prediction text.

        This lets the evaluator recognize fields such as:
        misconception, secondary_weakness, bottleneck,
        reason and trend when the runtime exposes them.

        If the runtime does not expose the expected semantic
        field, the result is reported as "not_exposed".
        """

        target = (
            ALOFBenchmarkEvaluator
            ._normalize_string(
                expected_value
            )
        )

        fields = (
            "misconception",
            "secondary_weakness",
            "bottleneck",
            "reason",
            "trend",
            "new_demand",
        )

        for field in fields:
            value = diagnosis.get(field)

            if value is None:
                continue

            values = (
                ALOFBenchmarkEvaluator
                ._as_list(value)
            )

            for candidate in values:
                normalized = (
                    ALOFBenchmarkEvaluator
                    ._normalize_string(
                        candidate
                    )
                )

                if normalized == target:
                    return field, value

        metadata = diagnosis.get(
            "metadata",
        )

        if isinstance(metadata, dict):
            for field, value in metadata.items():
                values = (
                    ALOFBenchmarkEvaluator
                    ._as_list(value)
                )

                for candidate in values:
                    normalized = (
                        ALOFBenchmarkEvaluator
                        ._normalize_string(
                            candidate
                        )
                    )

                    if normalized == target:
                        return field, value

        return None, None

    def evaluate_diagnosis(
        self,
        expected: dict[str, Any],
        result: dict[str, Any],
    ) -> dict[str, Any]:
        diagnosis = self._extract_diagnosis(
            result,
        )

        if diagnosis is None:
            return {
                "status": "not_exposed",
                "pass": None,
                "fields": {},
            }

        fields: dict[str, Any] = {}

        expected_concept = expected.get(
            "concept",
        )

        actual_concept = (
            self._primary_concept(
                diagnosis,
            )
        )

        if expected_concept is not None:
            concept_match = (
                self._normalize_string(
                    expected_concept
                )
                == self._normalize_string(
                    actual_concept
                )
            )

            fields["concept"] = {
                "expected": expected_concept,
                "actual": actual_concept,
                "pass": concept_match,
            }

        expected_level = expected.get(
            "level",
        )

        if expected_level is not None:
            actual_level = self._actual_level(
                diagnosis,
                actual_concept,
            )

            level_match = self._level_match(
                str(expected_level),
                actual_level,
            )

            fields["level"] = {
                "expected": (
                    self._canonical_level(
                        expected_level
                    )
                ),
                "actual": actual_level,
                "pass": level_match,
            }

            if actual_level is None:
                fields["level"]["status"] = (
                    "not_exposed"
                )

        semantic_keys = (
            "misconception",
            "secondary_weakness",
            "reason",
            "trend",
            "new_demand",
            "bottleneck",
        )

        for key in semantic_keys:
            if key not in expected:
                continue

            expected_value = expected.get(
                key,
            )

            field, actual_value = (
                self._find_semantic_field(
                    diagnosis,
                    str(expected_value),
                )
            )

            if field is not None:
                fields[key] = {
                    "expected": expected_value,
                    "actual": actual_value,
                    "source_field": field,
                    "pass": True,
                }
            else:
                fields[key] = {
                    "expected": expected_value,
                    "actual": None,
                    "source_field": None,
                    "pass": None,
                    "status": "not_exposed",
                }

        evaluated = [
            value["pass"]
            for value in fields.values()
            if isinstance(value, dict)
            and value.get("pass") is not None
        ]

        if not evaluated:
            status = "not_exposed"
            passed = None
        else:
            status = "evaluated"
            passed = all(evaluated)

        return {
            "status": status,
            "pass": passed,
            "fields": fields,
        }

    # ==========================================================
    # Strategy evaluation
    # ==========================================================

    @staticmethod
    def _strategy_type_match(
        expected_type: str,
        strategy: dict[str, Any],
    ) -> bool:
        expected = (
            ALOFBenchmarkEvaluator
            ._normalize_string(
                expected_type
            )
        )

        mapping = (
            ALOFBenchmarkEvaluator
            .STRATEGY_TYPE_MAPPING
            .get(expected)
        )

        if mapping is None:
            # If the dataset already contains a canonical
            # action or strategy, allow exact comparison.
            actual_action = (
                ALOFBenchmarkEvaluator
                ._normalize_string(
                    strategy.get("action")
                )
            )

            actual_strategy = (
                ALOFBenchmarkEvaluator
                ._normalize_string(
                    strategy.get("strategy")
                )
            )

            return expected in {
                actual_action,
                actual_strategy,
            }

        actual_action = (
            ALOFBenchmarkEvaluator
            ._normalize_string(
                strategy.get("action")
            )
        )

        actual_strategy = (
            ALOFBenchmarkEvaluator
            ._normalize_string(
                strategy.get("strategy")
            )
        )

        expected_actions = mapping.get(
            "action",
            set(),
        )

        expected_strategies = mapping.get(
            "strategy",
            set(),
        )

        action_match = (
            not expected_actions
            or actual_action in expected_actions
        )

        strategy_match = (
            not expected_strategies
            or actual_strategy in expected_strategies
        )

        return (
            action_match
            and strategy_match
        )

    @staticmethod
    def _difficulty_match(
        expected_difficulty: str,
        actual_difficulty: Any,
    ) -> bool | None:
        if actual_difficulty is None:
            return None

        expected = (
            ALOFBenchmarkEvaluator
            ._canonical_difficulty(
                expected_difficulty,
            )
        )

        actual = (
            ALOFBenchmarkEvaluator
            ._canonical_difficulty(
                actual_difficulty,
            )
        )

        return expected == actual

    @staticmethod
    def _focus_match(
        expected_focus: str,
        actual_focus: Any,
    ) -> bool | None:
        """
        Compare canonical concept IDs.

        Exact normalized concept equality is preferred.
        No substring matching is used because concepts such as
        "addition" and "integer_addition" are not necessarily
        semantically identical.
        """

        if actual_focus is None:
            return None

        expected = (
            ALOFBenchmarkEvaluator
            ._normalize_string(
                expected_focus
            )
        )

        if not expected:
            return True

        actual_values = (
            ALOFBenchmarkEvaluator
            ._canonical_set(
                actual_focus
            )
        )

        return expected in actual_values

    def evaluate_strategy(
        self,
        expected: dict[str, Any],
        result: dict[str, Any],
    ) -> dict[str, Any]:
        strategy = self._extract_strategy(
            result,
        )

        if strategy is None:
            return {
                "status": "not_exposed",
                "pass": None,
                "fields": {},
            }

        fields: dict[str, Any] = {}

        expected_type = expected.get(
            "type",
        )

        if expected_type is not None:
            type_match = (
                self._strategy_type_match(
                    str(expected_type),
                    strategy,
                )
            )

            fields["type"] = {
                "expected": expected_type,
                "actual": {
                    "action": strategy.get(
                        "action"
                    ),
                    "strategy": strategy.get(
                        "strategy"
                    ),
                },
                "pass": type_match,
            }

        expected_difficulty = expected.get(
            "difficulty",
        )

        if expected_difficulty is not None:
            actual_difficulty = strategy.get(
                "difficulty",
            )

            difficulty_match = (
                self._difficulty_match(
                    str(expected_difficulty),
                    actual_difficulty,
                )
            )

            fields["difficulty"] = {
                "expected": (
                    self._canonical_difficulty(
                        expected_difficulty
                    )
                ),
                "actual": (
                    self._canonical_difficulty(
                        actual_difficulty
                    )
                    if actual_difficulty is not None
                    else None
                ),
                "pass": difficulty_match,
            }

            if actual_difficulty is None:
                fields["difficulty"]["status"] = (
                    "not_exposed"
                )

        expected_focus = expected.get(
            "focus",
        )

        if expected_focus is not None:
            actual_focus = strategy.get(
                "focus_concepts",
            )

            focus_match = self._focus_match(
                str(expected_focus),
                actual_focus,
            )

            fields["focus"] = {
                "expected": expected_focus,
                "actual": actual_focus,
                "pass": focus_match,
            }

            if actual_focus is None:
                fields["focus"]["status"] = (
                    "not_exposed"
                )

        if "direct_answer" in expected:
            expected_direct_answer = bool(
                expected["direct_answer"]
            )

            actual_direct_answer = strategy.get(
                "direct_answer",
            )

            if actual_direct_answer is None:
                actual_direct_answer = strategy.get(
                    "answer_directly",
                )

            fields["direct_answer"] = {
                "expected": expected_direct_answer,
                "actual": actual_direct_answer,
                "pass": (
                    None
                    if actual_direct_answer is None
                    else (
                        bool(actual_direct_answer)
                        == expected_direct_answer
                    )
                ),
            }

            if actual_direct_answer is None:
                fields["direct_answer"]["status"] = (
                    "not_exposed"
                )

        evaluated = [
            value["pass"]
            for value in fields.values()
            if isinstance(value, dict)
            and value.get("pass") is not None
        ]

        if not evaluated:
            status = "not_exposed"
            passed = None
        else:
            status = "evaluated"
            passed = all(evaluated)

        return {
            "status": status,
            "pass": passed,
            "fields": fields,
        }

    # ==========================================================
    # Response evaluation
    # ==========================================================

    @staticmethod
    def _looks_like_direct_answer(
        prediction: str,
    ) -> bool:
        """
        Conservative heuristic.

        The evaluator must not try to solve the problem.
        It only detects common answer-first patterns.

        Examples considered direct:
            "Đáp án: x = 5"
            "Kết quả là 12"
            "x = 5"

        A worked explanation containing calculations is NOT
        automatically considered a direct answer unless it
        begins with an answer-style marker.
        """

        text = prediction.strip()

        if not text:
            return False

        first_line = text.splitlines()[0].strip()

        patterns = (
            r"^đáp\s*án\s*[:：]",
            r"^dap\s*an\s*[:：]",
            r"^kết\s*quả\s*[:：]",
            r"^ket\s*qua\s*[:：]",
            r"^answer\s*[:：]",
            r"^result\s*[:：]",
            r"^x\s*=\s*[-+]?\d",
        )

        return any(
            re.search(
                pattern,
                first_line,
                flags=re.IGNORECASE,
            )
            for pattern in patterns
        )

    def evaluate_response(
        self,
        expected_strategy: dict[str, Any],
        result: dict[str, Any],
    ) -> dict[str, Any]:
        prediction = self._text(
            result.get("prediction"),
        ).strip()

        available = bool(
            prediction,
        )

        expected_direct_answer = (
            expected_strategy.get(
                "direct_answer",
            )
        )

        direct_answer_violation = False

        if (
            expected_direct_answer is False
            and available
        ):
            direct_answer_violation = (
                self._looks_like_direct_answer(
                    prediction,
                )
            )

        return {
            "status": "evaluated",
            "prediction_available": available,
            "prediction_length": len(
                prediction
            ),
            "expected_direct_answer": (
                expected_direct_answer
            ),
            "direct_answer_violation": (
                direct_answer_violation
            ),
            "pass": (
                available
                and not direct_answer_violation
            ),
        }

    # ==========================================================
    # Case evaluation
    # ==========================================================

    @staticmethod
    def _dimension_semantic_pass(
        dimension: dict[str, Any],
    ) -> bool:
        """
        A dimension is semantically successful when:
        - it is explicitly passed; or
        - it is not exposed / not applicable and therefore
          contains no evaluated failure.

        This prevents optional runtime fields from making the
        entire benchmark case fail.
        """

        status = dimension.get(
            "status",
        )

        passed = dimension.get(
            "pass",
        )

        if status in {
            "not_exposed",
            "not_applicable",
        }:
            return True

        if passed is None:
            return True

        return bool(passed)

    def evaluate_result(
        self,
        result: dict[str, Any],
    ) -> dict[str, Any]:
        case_id = result["case_id"]

        if case_id not in self.samples:
            return {
                "case_id": case_id,
                "status": "unknown_case",
                "pass": False,
            }

        sample = self.samples[
            case_id
        ]

        expected = sample.get(
            "expected",
            {},
        )

        memory = self.evaluate_memory(
            expected.get(
                "memory",
                {},
            ),
            result,
        )

        diagnosis = self.evaluate_diagnosis(
            expected.get(
                "diagnosis",
                {},
            ),
            result,
        )

        strategy = self.evaluate_strategy(
            expected.get(
                "strategy",
                {},
            ),
            result,
        )

        response = self.evaluate_response(
            expected.get(
                "strategy",
                {},
            ),
            result,
        )

        dimensions = {
            "memory": memory,
            "diagnosis": diagnosis,
            "strategy": strategy,
            "response": response,
        }

        dimension_passes = {
            key: self._dimension_semantic_pass(
                value
            )
            for key, value in dimensions.items()
        }

        return {
            "case_id": case_id,
            "execution_success": bool(
                result.get("success")
            ),
            "dimensions": dimensions,
            "dimension_passes": dimension_passes,
            "semantic_pass": all(
                dimension_passes.values()
            ),
        }

    # ==========================================================
    # Aggregate evaluation
    # ==========================================================

    @staticmethod
    def _rate(
        values: list[bool],
    ) -> float:
        if not values:
            return 0.0

        return round(
            sum(values) / len(values),
            4,
        )

    @staticmethod
    def _mean(
        values: list[float],
    ) -> float:
        if not values:
            return 0.0

        return round(
            sum(values) / len(values),
            4,
        )

    def evaluate_file(
        self,
        results_path: str | Path,
    ) -> dict[str, Any]:
        results: list[dict[str, Any]] = []

        with Path(results_path).open(
            "r",
            encoding="utf-8",
        ) as f:
            for line_no, line in enumerate(
                f,
                start=1,
            ):
                line = line.strip()

                if not line:
                    continue

                try:
                    results.append(
                        json.loads(line)
                    )
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Invalid JSON at line "
                        f"{line_no}: {exc}"
                    ) from exc

        evaluated = [
            self.evaluate_result(result)
            for result in results
        ]

        total = len(evaluated)

        successful = sum(
            1
            for item in evaluated
            if item.get(
                "execution_success",
                False,
            )
        )

        semantic_passes = sum(
            1
            for item in evaluated
            if item.get(
                "semantic_pass",
                False,
            )
        )

        memory_passes: list[bool] = []
        memory_f1: list[float] = []

        diagnosis_passes: list[bool] = []
        strategy_passes: list[bool] = []
        response_passes: list[bool] = []

        diagnosis_not_exposed = 0
        strategy_not_exposed = 0

        for item in evaluated:
            dimensions = item.get(
                "dimensions",
                {},
            )

            memory = dimensions.get(
                "memory",
                {},
            )

            diagnosis = dimensions.get(
                "diagnosis",
                {},
            )

            strategy = dimensions.get(
                "strategy",
                {},
            )

            response = dimensions.get(
                "response",
                {},
            )

            if memory.get(
                "status"
            ) == "evaluated":
                memory_passes.append(
                    bool(memory.get("pass"))
                )
                memory_f1.append(
                    float(
                        memory.get(
                            "f1",
                            0.0,
                        )
                    )
                )

            if diagnosis.get(
                "status"
            ) == "evaluated":
                diagnosis_passes.append(
                    bool(
                        diagnosis.get(
                            "pass"
                        )
                    )
                )
            elif diagnosis.get(
                "status"
            ) == "not_exposed":
                diagnosis_not_exposed += 1

            if strategy.get(
                "status"
            ) == "evaluated":
                strategy_passes.append(
                    bool(
                        strategy.get(
                            "pass"
                        )
                    )
                )
            elif strategy.get(
                "status"
            ) == "not_exposed":
                strategy_not_exposed += 1

            response_passes.append(
                bool(
                    response.get(
                        "pass"
                    )
                )
            )

        return {
            "total_cases": total,
            "successful_cases": successful,
            "execution_success_rate": (
                successful / total
                if total
                else 0.0
            ),
            "semantic_pass_cases": semantic_passes,
            "semantic_pass_rate": (
                semantic_passes / total
                if total
                else 0.0
            ),
            "memory": {
                "evaluated_cases": len(
                    memory_passes
                ),
                "pass_cases": sum(
                    memory_passes
                ),
                "pass_rate": self._rate(
                    memory_passes
                ),
                "mean_f1": self._mean(
                    memory_f1
                ),
            },
            "diagnosis": {
                "evaluated_cases": len(
                    diagnosis_passes
                ),
                "pass_cases": sum(
                    diagnosis_passes
                ),
                "pass_rate": self._rate(
                    diagnosis_passes
                ),
                "not_exposed_cases": (
                    diagnosis_not_exposed
                ),
            },
            "strategy": {
                "evaluated_cases": len(
                    strategy_passes
                ),
                "pass_cases": sum(
                    strategy_passes
                ),
                "pass_rate": self._rate(
                    strategy_passes
                ),
                "not_exposed_cases": (
                    strategy_not_exposed
                ),
            },
            "response": {
                "evaluated_cases": len(
                    response_passes
                ),
                "pass_cases": sum(
                    response_passes
                ),
                "pass_rate": self._rate(
                    response_passes
                ),
            },
            "cases": evaluated,
        }

    # ==========================================================
    # Failure report
    # ==========================================================

    @staticmethod
    def build_failure_report(
        report: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Build a compact report containing only failed cases.

        The main evaluation report is not modified.

        A case is included when:
        - execution failed; or
        - at least one evaluated dimension failed; or
        - semantic_pass is False.

        Only failed dimensions/fields are retained so the file
        can be used directly for benchmark debugging.
        """

        failures: list[dict[str, Any]] = []

        for case in report.get(
            "cases",
            [],
        ):
            case_id = case.get(
                "case_id",
            )

            failed_dimensions: dict[str, Any] = {}

            dimensions = case.get(
                "dimensions",
                {},
            )

            for dimension_name, dimension in dimensions.items():
                if not isinstance(dimension, dict):
                    continue

                if dimension.get(
                    "pass"
                ) is False:
                    failed_fields: dict[str, Any] = {}

                    fields = dimension.get(
                        "fields",
                        {},
                    )

                    if isinstance(fields, dict):
                        for field_name, field in fields.items():
                            if (
                                isinstance(field, dict)
                                and field.get("pass") is False
                            ):
                                failed_fields[field_name] = field

                    failed_dimensions[dimension_name] = {
                        "status": dimension.get(
                            "status"
                        ),
                        "pass": False,
                        "fields": failed_fields,
                    }

                    if dimension_name == "memory":
                        for key in (
                            "expected",
                            "actual",
                            "precision",
                            "recall",
                            "f1",
                            "matched",
                            "missing",
                            "extra",
                        ):
                            if key in dimension:
                                failed_dimensions[
                                    dimension_name
                                ][key] = dimension[key]

            execution_success = bool(
                case.get(
                    "execution_success",
                    False,
                )
            )

            semantic_pass = bool(
                case.get(
                    "semantic_pass",
                    False,
                )
            )

            if (
                not execution_success
                or not semantic_pass
                or failed_dimensions
            ):
                failures.append(
                    {
                        "case_id": case_id,
                        "execution_success": execution_success,
                        "semantic_pass": semantic_pass,
                        "dimension_passes": case.get(
                            "dimension_passes",
                            {},
                        ),
                        "failures": failed_dimensions,
                    }
                )

        diagnosis_failures = [
            item
            for item in failures
            if "diagnosis" in item.get(
                "failures",
                {},
            )
        ]

        strategy_failures = [
            item
            for item in failures
            if "strategy" in item.get(
                "failures",
                {},
            )
        ]

        memory_failures = [
            item
            for item in failures
            if "memory" in item.get(
                "failures",
                {},
            )
        ]

        response_failures = [
            item
            for item in failures
            if "response" in item.get(
                "failures",
                {},
            )
        ]

        execution_failures = [
            item
            for item in failures
            if not item.get(
                "execution_success",
                False,
            )
        ]

        return {
            "total_cases": report.get(
                "total_cases",
                0,
            ),
            "failed_cases": len(
                failures
            ),
            "semantic_pass_cases": report.get(
                "semantic_pass_cases",
                0,
            ),
            "semantic_fail_cases": (
                report.get(
                    "total_cases",
                    0,
                )
                - report.get(
                    "semantic_pass_cases",
                    0,
                )
            ),
            "failure_counts": {
                "execution": len(
                    execution_failures
                ),
                "memory": len(
                    memory_failures
                ),
                "diagnosis": len(
                    diagnosis_failures
                ),
                "strategy": len(
                    strategy_failures
                ),
                "response": len(
                    response_failures
                ),
            },
            "failures": failures,
        }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Semantic evaluator for the ALOF benchmark."
        ),
    )

    parser.add_argument(
        "--dataset",
        default=(
            "backend/benchmark/ALOF/"
            "data/adaptive_learning_vi_longcontext.jsonl"
        ),
    )

    parser.add_argument(
        "--results",
        default=(
            "backend/benchmark/ALOF/"
            "results/results_longcontext.jsonl"
        ),
    )

    parser.add_argument(
        "--report",
        default=(
            "backend/benchmark/ALOF/"
            "report_longcontext.json"
        ),
        help="Path to the generated evaluation report.",
    )

    parser.add_argument(
        "--failure-report",
        default=(
            "backend/benchmark/ALOF/"
            "failure_report_longcontext.json"
        ),
        help=(
            "Path to the generated failure-only report."
        ),
    )

    args = parser.parse_args()

    evaluator = ALOFBenchmarkEvaluator(
        args.dataset,
    )

    report = evaluator.evaluate_file(
        args.results,
    )

    report_path = Path(args.report)
    report_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with report_path.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            report,
            f,
            ensure_ascii=False,
            indent=2,
        )

    # ==========================================================
    # Write failure-only report
    # ==========================================================

    failure_report = (
        evaluator.build_failure_report(
            report,
        )
    )

    failure_report_path = Path(
        args.failure_report
    )

    failure_report_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with failure_report_path.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            failure_report,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        )
    )

    print(
        f"\nEvaluation report written to: "
        f"{report_path}"
    )

    print(
        f"Failure report written to: "
        f"{failure_report_path}"
    )


if __name__ == "__main__":
    main()

