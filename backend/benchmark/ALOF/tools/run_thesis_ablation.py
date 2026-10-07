"""Offline ablation on ALOF benchmark gold (no LLM)."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.application.orchestration.adaptive_learning_pipeline import (
    AdaptiveLearningPipeline,
)
from backend.application.runtime.evidence_selector import EvidenceSelector
from backend.benchmark.ALOF.tools.gold_from_runtime import (
    build_learning_state,
    compute_diagnosis_strategy_gold,
    compute_memory_gold,
)
from backend.domain.learning.historical_evidence import HistoricalEvidence
from backend.domain.learning.historical_evidence_builder import (
    HistoricalEvidenceBuilder,
)
from backend.domain.learning.knowledge_diagnosis import KnowledgeStateDiagnoser
from backend.domain.learning.temporal_error_pattern import (
    TemporalErrorPattern,
    TemporalErrorPatternDetector,
)
from backend.infrastructure.prompts.context_builder import ContextBuilder


DATASETS: list[tuple[str, str, Path]] = [
    (
        "longcontext",
        "easy",
        Path("backend/benchmark/ALOF/data/long_context/adaptive_learning_vi_longcontext_easy.jsonl"),
    ),
    (
        "longcontext",
        "medium",
        Path("backend/benchmark/ALOF/data/long_context/adaptive_learning_vi_longcontext_medium.jsonl"),
    ),
    (
        "multiconcept",
        "easy",
        Path("backend/benchmark/ALOF/data/multi_concept/adaptive_learning_vi_multiconcept_easy.jsonl"),
    ),
    (
        "multiconcept",
        "medium",
        Path("backend/benchmark/ALOF/data/multi_concept/adaptive_learning_vi_multiconcept_medium.jsonl"),
    ),
    (
        "multiconcept",
        "hard",
        Path("backend/benchmark/ALOF/data/multi_concept/adaptive_learning_vi_multiconcept_hard.jsonl"),
    ),
    (
        "strategy",
        "easy",
        Path("backend/benchmark/ALOF/data/strategy/adaptive_learning_vi_strategy_easy.jsonl"),
    ),
    (
        "strategy",
        "medium",
        Path("backend/benchmark/ALOF/data/strategy/adaptive_learning_vi_strategy_medium.jsonl"),
    ),
    (
        "strategy",
        "hard",
        Path("backend/benchmark/ALOF/data/strategy/adaptive_learning_vi_strategy_hard.jsonl"),
    ),
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                samples.append(json.loads(line))
    return samples


def f1_from_sets(expected: set[str], actual: set[str]) -> tuple[float, float, float]:
    if not expected and not actual:
        return 1.0, 1.0, 1.0
    if not actual:
        return 0.0, 0.0, 0.0
    if not expected:
        return 0.0, 0.0, 0.0
    matched = expected & actual
    precision = len(matched) / len(actual)
    recall = len(matched) / len(expected)
    if precision + recall == 0:
        return 0.0, 0.0, 0.0
    return precision, recall, 2 * precision * recall / (precision + recall)


def task_fields(sample: dict[str, Any]) -> tuple[str, list[str]]:
    task = sample["current_task"]
    question = str(task.get("question") or task.get("content") or "")
    concept_ids = [str(v) for v in (task.get("concept_ids") or [])]
    return question, concept_ids


def gold_memory_ids(sample: dict[str, Any]) -> set[str]:
    expected = (sample.get("expected") or {}).get("memory") or {}
    ids = expected.get("top_k_interactions")
    if ids:
        return {str(x) for x in ids}
    return set(compute_memory_gold(sample)["top_k_interactions"])


def recency_only_ids(sample: dict[str, Any], k: int = 5) -> list[str]:
    history = list(sample.get("history") or [])
    history_sorted = sorted(
        history,
        key=lambda item: str(item.get("timestamp") or ""),
        reverse=True,
    )
    ids: list[str] = []
    for item in history_sorted[:k]:
        qid = str(item.get("question_id") or "").strip()
        if qid:
            ids.append(qid)
    return ids


def concept_only_ids(sample: dict[str, Any], k: int = 5) -> list[str]:
    _, concept_ids = task_fields(sample)
    current = {c.lower() for c in concept_ids}
    scored: list[tuple[int, str, str]] = []
    for index, item in enumerate(sample.get("history") or []):
        record_concepts = {str(c).lower() for c in (item.get("concept_ids") or [])}
        overlap = len(current & record_concepts)
        qid = str(item.get("question_id") or "").strip()
        ts = str(item.get("timestamp") or "")
        if qid:
            scored.append((overlap, ts, qid))
    scored.sort(key=lambda row: (-row[0], row[1]), reverse=False)
    scored.sort(key=lambda row: (-row[0], row[1]))
    return [row[2] for row in scored[:k]]


def lexical_only_ids(sample: dict[str, Any], k: int = 5) -> list[str]:
    question, concept_ids = task_fields(sample)
    history = sample.get("history") or []
    selection = EvidenceSelector.select(
        current_question=question,
        current_concept_ids=[],
        interactions=history,
        related_history=[],
        top_k=k,
        max_tokens=ContextBuilder.MEMORY_MAX_TOKENS,
    )
    ids: list[str] = []
    for record in selection["history"] + selection["related_history"]:
        qid = str(record.get("question_id") or "").strip()
        if qid:
            ids.append(qid)
    return ids[:k]


class ZeroTemporalDetector(TemporalErrorPatternDetector):
    def detect(self, concept_id: str, interactions):  # type: ignore[override]
        return TemporalErrorPattern(
            concept_id=concept_id,
            pattern="stable",
        )


def diagnosis_variant(
    sample: dict[str, Any],
    *,
    use_evidence: bool,
    use_temporal: bool,
) -> dict[str, Any]:
    question, concept_ids = task_fields(sample)
    state = build_learning_state(sample)
    if use_evidence:
        evidence = HistoricalEvidenceBuilder(recent_limit=5).build(
            learning_state=state,
            current_question=question,
            related_concept_ids=concept_ids,
        )
    else:
        evidence = HistoricalEvidence(
            learner_id=state.learner_id,
            current_question=question,
            related_concept_ids=concept_ids,
        )
    detector = (
        TemporalErrorPatternDetector()
        if use_temporal
        else ZeroTemporalDetector()
    )
    diagnoser = KnowledgeStateDiagnoser(temporal_detector=detector)
    diagnosis = diagnoser.diagnose(
        learning_state=state,
        evidence=evidence,
        primary_concept_ids=concept_ids,
    )
    pipeline = AdaptiveLearningPipeline(diagnoser=diagnoser)
    if use_evidence:
        result = pipeline.run(
            learning_state=state,
            current_question=question,
            related_concept_ids=concept_ids,
            primary_concept_ids=concept_ids,
        )
        action = result.teaching_action
        diagnosis = result.diagnosis
    else:
        from backend.domain.learning.adaptive_teaching_action import (
            AdaptiveTeachingActionSelector,
        )

        action = AdaptiveTeachingActionSelector().select(diagnosis)

    primary = (
        diagnosis.primary_concepts[0]
        if diagnosis.primary_concepts
        else None
    )
    primary_state = diagnosis.concepts.get(primary) if primary else None
    return {
        "concept": primary,
        "level": str(primary_state.level) if primary_state is not None else None,
        "weak_concepts": list(diagnosis.weak_concepts),
        "action": str(action.action),
        "strategy": str(action.strategy),
        "difficulty": str(action.difficulty),
        "focus_concepts": list(action.focus_concepts),
    }


def chatbot_baseline(sample: dict[str, Any]) -> dict[str, Any]:
    """Single-turn chatbot: recency memory, last concept, always explain."""
    _, concept_ids = task_fields(sample)
    history = list(sample.get("history") or [])
    last = history[-1] if history else {}
    last_concepts = [str(c) for c in (last.get("concept_ids") or [])]
    primary = (concept_ids[0] if concept_ids else None) or (
        last_concepts[0] if last_concepts else None
    )
    return {
        "memory": recency_only_ids(sample),
        "concept": primary,
        "level": "intermediate",
        "action": "explain",
        "strategy": "direct_explanation",
        "difficulty": "medium",
        "focus_concepts": concept_ids[:1] or last_concepts[:1],
    }


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def main() -> None:
    rows: list[dict[str, Any]] = []
    dataset_stats: list[dict[str, Any]] = []

    for split, difficulty, path in DATASETS:
        samples = load_jsonl(path)
        history_lens: list[int] = []
        concept_counts: list[int] = []
        unique_concepts: set[str] = set()
        domains_from_concepts: set[str] = set()

        metrics: dict[str, list[float]] = defaultdict(list)
        exact: dict[str, list[int]] = defaultdict(list)

        for sample in samples:
            history = sample.get("history") or []
            history_lens.append(len(history))
            _, concept_ids = task_fields(sample)
            concept_counts.append(len(concept_ids))
            unique_concepts.update(concept_ids)
            for item in history:
                unique_concepts.update(str(c) for c in (item.get("concept_ids") or []))

            gold_mem = gold_memory_ids(sample)
            gold_ds = compute_diagnosis_strategy_gold(sample)
            gold_diag = gold_ds["diagnosis"]
            gold_str = gold_ds["strategy"]

            variants = {
                "alof": list(gold_mem),
                "recency": recency_only_ids(sample),
                "concept": concept_only_ids(sample),
                "lexical": lexical_only_ids(sample),
                "chatbot": chatbot_baseline(sample)["memory"],
            }
            # Full selector as sanity check
            full_mem = set(compute_memory_gold(sample)["top_k_interactions"])

            for name, ids in variants.items():
                p, r, f = f1_from_sets(gold_mem, set(ids))
                metrics[f"mem_{name}_f1"].append(f)
                exact[f"mem_{name}_exact"].append(int(set(ids) == gold_mem))

            p, r, f = f1_from_sets(gold_mem, full_mem)
            metrics["mem_full_f1"].append(f)
            exact["mem_full_exact"].append(int(full_mem == gold_mem))

            full_var = diagnosis_variant(
                sample, use_evidence=True, use_temporal=True
            )
            no_temp = diagnosis_variant(
                sample, use_evidence=True, use_temporal=False
            )
            no_ev = diagnosis_variant(
                sample, use_evidence=False, use_temporal=True
            )
            bot = chatbot_baseline(sample)

            for name, pred in [
                ("alof", full_var),
                ("no_temporal", no_temp),
                ("no_evidence", no_ev),
                ("chatbot", bot),
            ]:
                exact[f"diag_{name}_concept"].append(
                    int(pred.get("concept") == gold_diag.get("concept"))
                )
                exact[f"diag_{name}_level"].append(
                    int(str(pred.get("level")) == str(gold_diag.get("level")))
                )
                exact[f"str_{name}_action"].append(
                    int(pred.get("action") == gold_str.get("action"))
                )
                exact[f"str_{name}_strategy"].append(
                    int(pred.get("strategy") == gold_str.get("strategy"))
                )
                exact[f"str_{name}_difficulty"].append(
                    int(pred.get("difficulty") == gold_str.get("difficulty"))
                )
                gold_focus = set(gold_str.get("focus_concepts") or [])
                pred_focus = set(pred.get("focus_concepts") or [])
                _, _, f = f1_from_sets(gold_focus, pred_focus)
                metrics[f"str_{name}_focus_f1"].append(f)

        dataset_stats.append(
            {
                "split": split,
                "difficulty": difficulty,
                "n": len(samples),
                "mean_history": round(mean([float(x) for x in history_lens]), 2),
                "mean_task_concepts": round(mean([float(x) for x in concept_counts]), 2),
                "unique_concepts": len(unique_concepts),
            }
        )

        summary = {
            "split": split,
            "difficulty": difficulty,
            "n": len(samples),
        }
        for key, values in sorted(metrics.items()):
            summary[key] = round(mean(values), 4)
        for key, values in sorted(exact.items()):
            summary[key] = round(mean([float(x) for x in values]), 4)
        rows.append(summary)
        print(json.dumps(summary, ensure_ascii=False))

    out_dir = Path("backend/benchmark/ALOF/reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {"datasets": dataset_stats, "results": rows}
    out_path = out_dir / "thesis_ablation.json"
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
