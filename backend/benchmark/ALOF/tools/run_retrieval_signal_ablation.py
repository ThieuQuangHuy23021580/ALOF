"""Signal-level retrieval ablation for ALOF (offline, no LLM).

Why this script exists
----------------------
`expected.memory.top_k_interactions` in the ALOF datasets is *runtime-derived*
(see DATASET_RULES.md sec.14 "runtime is the source of truth").  After the
topK=8 sweep that field holds 8 ids for most cases, so scoring the K=5
runtime against it measures a K mismatch, not retrieval quality.

This script therefore evaluates every retrieval configuration against an
*independent* gold: the concept-overlap relevant set, which is defined by the
dataset rules before any ranking function is applied.

The scorer reuses EvidenceSelector's own feature helpers unchanged, so the
"full" configuration reproduces EvidenceSelector.select exactly.  Only the
weight vector changes between configurations.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.application.runtime.evidence_selector import (  # noqa: E402
    EvidenceSelector,
)
from backend.benchmark.ALOF.tools.gold_from_runtime import (  # noqa: E402
    build_learning_state,
    parse_timestamp,
    select_memory,
)
from backend.domain.learning.historical_evidence_builder import (  # noqa: E402
    HistoricalEvidenceBuilder,
)
from backend.infrastructure.prompts.context_builder import (  # noqa: E402
    ContextBuilder,
)

DATASETS = [
    ("longcontext", "easy", "data/long_context/adaptive_learning_vi_longcontext_easy.jsonl"),
    ("longcontext", "medium", "data/long_context/adaptive_learning_vi_longcontext_medium.jsonl"),
    ("multiconcept", "easy", "data/multi_concept/adaptive_learning_vi_multiconcept_easy.jsonl"),
    ("multiconcept", "medium", "data/multi_concept/adaptive_learning_vi_multiconcept_medium.jsonl"),
    ("multiconcept", "hard", "data/multi_concept/adaptive_learning_vi_multiconcept_hard.jsonl"),
    ("strategy", "easy", "data/strategy/adaptive_learning_vi_strategy_easy.jsonl"),
    ("strategy", "medium", "data/strategy/adaptive_learning_vi_strategy_medium.jsonl"),
    ("strategy", "hard", "data/strategy/adaptive_learning_vi_strategy_hard.jsonl"),
]

BASE = ROOT / "backend" / "benchmark" / "ALOF"

# EvidenceSelector._score_record weights, exposed as a configurable vector.
#   score = 20*|qid_overlap| + 8*|concept_overlap| + 5*date + 5*lexical
#         + correctness + 2*recency
FULL_WEIGHTS = {
    "qid": 20.0,
    "concept": 8.0,
    "date": 5.0,
    "lexical": 5.0,
    "correctness": 1.0,
    "recency": 2.0,
}

CONFIGS: dict[str, dict[str, float]] = {
    "ALOF-full": FULL_WEIGHTS,
    "w/o-concept": {**FULL_WEIGHTS, "concept": 0.0},
    "w/o-error": {**FULL_WEIGHTS, "correctness": 0.0},
    "w/o-recency": {**FULL_WEIGHTS, "recency": 0.0},
    "w/o-semantic": {**FULL_WEIGHTS, "lexical": 0.0},
    "w/o-date": {**FULL_WEIGHTS, "date": 0.0},
    "recency-only": {
        "qid": 0.0, "concept": 0.0, "date": 0.0,
        "lexical": 0.0, "correctness": 0.0, "recency": 2.0,
    },
    "concept-only": {
        "qid": 0.0, "concept": 8.0, "date": 0.0,
        "lexical": 0.0, "correctness": 0.0, "recency": 0.0,
    },
    "lexical-only": {
        "qid": 0.0, "concept": 0.0, "date": 0.0,
        "lexical": 5.0, "correctness": 0.0, "recency": 0.0,
    },
}


# ----------------------------------------------------------------------
# Candidate pool: identical to select_memory(), so "full" is comparable
# ----------------------------------------------------------------------
def candidate_pool(sample: dict) -> tuple[str, list[str], list[dict], list[dict]]:
    task = sample["current_task"]
    question = str(task.get("question") or task.get("content") or "")
    concept_ids = [str(v) for v in (task.get("concept_ids") or [])]

    selection = select_memory(sample)
    state = build_learning_state(sample)
    evidence = HistoricalEvidenceBuilder(recent_limit=5).build(
        learning_state=state,
        current_question=question,
        related_concept_ids=concept_ids,
    )

    records: list[dict] = []
    seen: set[str] = set()
    for interaction in list(evidence.relevant_interactions) + list(
        evidence.recent_interactions
    ):
        if interaction.id in seen:
            continue
        seen.add(interaction.id)
        records.append(
            {
                "question_id": interaction.question_id,
                "question": interaction.question,
                "answer": interaction.answer,
                "correct": interaction.correct,
                "concept": list(interaction.concept_ids),
                "concept_ids": list(interaction.concept_ids),
                "timestamp": interaction.timestamp,
                "result": interaction.correct,
            }
        )

    # keep ordering used by the runtime: relevant first, then recent
    return question, concept_ids, records, list(evidence.related_interactions)


def independent_gold(sample: dict, records: list[dict]) -> set[str]:
    """Concept-overlap gold, independent of any ranking function."""
    task = sample["current_task"]
    current = {str(c).lower() for c in (task.get("concept_ids") or [])}
    if not current:
        return set()
    return {
        str(r.get("question_id"))
        for r in records
        if {str(c).lower() for c in (r.get("concept_ids") or [])} & current
    }


# ----------------------------------------------------------------------
# Parameterised scorer built on EvidenceSelector's own helpers
# ----------------------------------------------------------------------
def select_with_weights(
    records: list[dict],
    question: str,
    concept_ids: list[str],
    weights: dict[str, float],
    top_k: int = ContextBuilder.MEMORY_TOP_K,
    max_tokens: int = ContextBuilder.MEMORY_MAX_TOKENS,
) -> list[str]:
    cset = {c.lower() for c in concept_ids if c}
    total = len(records)

    q_ids = EvidenceSelector._extract_question_ids(question)
    scored: list[dict] = []
    for index, record in enumerate(records):
        text = EvidenceSelector._record_text(record)
        r_ids = EvidenceSelector._extract_question_ids(text)
        overlap = set(q_ids) & set(r_ids)
        c_overlap = cset & {
            v.lower() for v in EvidenceSelector._extract_concepts(record)
        }
        date = EvidenceSelector._date_overlap(question, text)
        lex = EvidenceSelector._lexical_overlap(question, text)
        corr = EvidenceSelector._correctness_score(record)
        recency = (index + 1) / max(total, 1)

        score = (
            weights["qid"] * len(overlap)
            + weights["concept"] * len(c_overlap)
            + weights["date"] * date
            + weights["lexical"] * lex
            + weights["correctness"] * corr
            + weights["recency"] * recency
        )
        scored.append(
            {
                "record": record,
                "score": score,
                "recency_rank": index,
                "original_index": index,
            }
        )

    scored.sort(
        key=lambda c: (
            -float(c["score"]),
            -int(c["recency_rank"]),
            int(c["original_index"]),
        )
    )

    selected: list[dict] = []
    keys: set[str] = set()
    used = 0
    for cand in scored:
        if len(selected) >= top_k:
            break
        rec = cand["record"]
        key = EvidenceSelector._dedupe_key(rec)
        if key in keys:
            continue
        cost = EvidenceSelector._estimate_tokens([rec])
        if cost <= 0 or used + cost > max_tokens:
            continue
        selected.append(rec)
        keys.add(key)
        used += cost

    out: list[str] = []
    for rec in selected:
        qid = str(rec.get("question_id") or "").strip()
        if qid:
            out.append(qid)
    return out


def recency_baseline(sample: dict, k: int) -> list[str]:
    hist = sorted(
        sample.get("history") or [],
        key=lambda r: parse_timestamp(r.get("timestamp")),
        reverse=True,
    )
    return [
        str(r.get("question_id"))
        for r in hist[:k]
        if r.get("question_id")
    ]


def prf(gold: set[str], pred: list[str]) -> tuple[float, float, float]:
    aset = set(pred)
    if not gold and not aset:
        return 1.0, 1.0, 1.0
    matched = gold & aset
    p = len(matched) / len(aset) if aset else 0.0
    r = len(matched) / len(gold) if gold else 0.0
    f = 2 * p * r / (p + r) if (p + r) else 0.0
    return p, r, f


def ndcg(gold: set[str], pred: list[str], k: int) -> float:
    if not gold:
        return 0.0
    dcg = sum(
        1.0 / math.log2(i + 2)
        for i, qid in enumerate(pred[:k])
        if qid in gold
    )
    ideal = sum(
        1.0 / math.log2(i + 2) for i in range(min(k, len(gold)))
    )
    return dcg / ideal if ideal else 0.0


def main() -> None:
    per_ds: list[dict] = []
    sanity_mismatch = 0
    sanity_total = 0

    for split, diff, rel in DATASETS:
        path = BASE / rel
        acc: dict[str, list[float]] = {}
        gold_sizes: list[int] = []

        for line in path.open(encoding="utf-8"):
            if not line.strip():
                continue
            sample = json.loads(line)
            question, concept_ids, records, _ = candidate_pool(sample)
            gold = independent_gold(sample, records)
            gold_sizes.append(len(gold))

            for name, w in CONFIGS.items():
                pred = select_with_weights(records, question, concept_ids, w)
                p, r, f = prf(gold, pred)
                acc.setdefault(f"{name}__P", []).append(p)
                acc.setdefault(f"{name}__R", []).append(r)
                acc.setdefault(f"{name}__F1", []).append(f)
                acc.setdefault(f"{name}__nDCG", []).append(
                    ndcg(gold, pred, ContextBuilder.MEMORY_TOP_K)
                )
                acc.setdefault(f"{name}__exact", []).append(
                    float(set(pred) == gold)
                )

            rb = recency_baseline(sample, ContextBuilder.MEMORY_TOP_K)
            p, r, f = prf(gold, rb)
            acc.setdefault("recency-baseline__P", []).append(p)
            acc.setdefault("recency-baseline__R", []).append(r)
            acc.setdefault("recency-baseline__F1", []).append(f)
            acc.setdefault("recency-baseline__nDCG", []).append(
                ndcg(gold, rb, ContextBuilder.MEMORY_TOP_K)
            )
            acc.setdefault("recency-baseline__exact", []).append(
                float(set(rb) == gold)
            )

            # sanity: does the full config reproduce EvidenceSelector.select?
            ref = select_memory(sample)
            ref_ids = [
                str(r.get("question_id") or "").strip()
                for r in ref["history"] + ref["related_history"]
            ]
            full_ids = select_with_weights(
                records, question, concept_ids, FULL_WEIGHTS
            )
            sanity_total += 1
            if set(ref_ids) != set(full_ids):
                sanity_mismatch += 1

        row: dict = {
            "split": split,
            "difficulty": diff,
            "n": len(gold_sizes),
            "mean_gold_size": round(mean(gold_sizes), 2),
        }
        for key, vals in acc.items():
            row[key] = round(mean(vals), 4)
        per_ds.append(row)
        print(json.dumps(row, ensure_ascii=False))

    out = {
        "metric_definitions": {
            "gold": "concept-overlap relevant set (independent of ranking)",
            "k": ContextBuilder.MEMORY_TOP_K,
            "note": (
                "top_k_interactions gold is runtime-derived and holds 8 ids "
                "after the topK=8 sweep; it is NOT used here."
            ),
        },
        "sanity_full_vs_evidence_selector": {
            "cases": sanity_total,
            "mismatch": sanity_mismatch,
        },
        "datasets": per_ds,
    }
    out_path = BASE / "reports" / "retrieval_signal_ablation.json"
    out_path.write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nwrote {out_path}")
    print(
        f"sanity: full-config vs EvidenceSelector.select -> "
        f"{sanity_mismatch} mismatch / {sanity_total} cases"
    )

    print("\n=== MACRO AVERAGES over 8 datasets ===")
    names = list(CONFIGS) + ["recency-baseline"]
    for metric in ("F1", "nDCG", "P", "R", "exact"):
        print(f"-- {metric}")
        for n in names:
            vals = [r[f"{n}__{metric}"] for r in per_ds]
            print(f"   {n:16s} {mean(vals):.4f}")


if __name__ == "__main__":
    main()
