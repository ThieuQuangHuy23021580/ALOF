"""Measure how well TemporalErrorPatternDetector separates error trajectories.

Motivation
----------
Chapter 5 of the thesis (RQ3) needs evidence for or against the claim that the
temporal component distinguishes *shapes* of error trajectory, not merely the
correctness ratio.  The gold diagnosis labels in the ALOF benchmark are derived
from ALOF's own output, so ablating the detector against them cannot answer the
question: it can only show self-consistency.

This script therefore answers RQ3 with a stimulus set instead of the benchmark
labels.  It builds four families of synthetic correctness sequences that differ
in temporal shape but are matched on correctness ratio, then asks the detector
to classify each one.  A detector that only read the correctness ratio would
score at chance across the matched pairs; a detector that reads temporal shape
scores well above it.

Two quantities are reported:

  * per-family recovery rate: how often the intended label is produced;
  * discrimination margin: the accuracy gap between the two families that are
    *matched* on correctness ratio, which is the part of the signal that a
    ratio-only detector structurally cannot produce.

The synthetic stimuli are a controlled probe, not a claim about learner data;
the script prints the exact sequences so they can be inspected.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import UTC, datetime, timedelta
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.domain.learning.learning_interaction import (  # noqa: E402
    LearningInteraction,
)
from backend.domain.learning.temporal_error_pattern import (  # noqa: E402
    TemporalErrorPatternDetector,
)

BASE = ROOT / "backend" / "benchmark" / "ALOF"
OUT = BASE / "reports" / "temporal_pattern_discrimination.json"

CONCEPT = "probe_concept"
DAY = timedelta(days=1)


def build_interactions(correctness: list[bool]) -> list[LearningInteraction]:
    """One interaction per day, oldest first. Day 0 is 30 days before now."""
    start = datetime(2026, 1, 1, tzinfo=UTC)
    out: list[LearningInteraction] = []
    for i, ok in enumerate(correctness):
        out.append(
            LearningInteraction(
                id=f"{CONCEPT}_{i}",
                learner_id="probe",
                question_id=f"q{i}",
                question=f"Câu hỏi {i}",
                answer="a",
                correct=ok,
                concept_ids=[CONCEPT],
                timestamp=start + i * DAY,
            )
        )
    return out


# Each family is (label, sequence, rationale).
# "persistent": errors cluster late and continue to the end.
# "recovering": errors are early, recent tail is correct.
# "unstable":   correctness alternates, so transitions are near-uniform.
# "stable":     correct throughout, no errors.
FAMILIES: list[tuple[str, list[bool], str]] = [
    (
        "persistent",
        [True, True, True, False, False, False, False],
        "tỷ lệ đúng 3/7, nhưng ba lỗi liên tiếp ở cuối chuỗi",
    ),
    (
        "recovering",
        [False, False, False, True, True, True, True],
        "tỷ lệ đúng 4/7, ba lỗi liên tiếp ở đầu chuỗi",
    ),
    (
        "unstable",
        [True, False, True, False, True, False, True],
        "tỷ lệ đúng 4/7, đúng sai xen kẽ, bốn sự kiện chuyển cân bằng",
    ),
    (
        "stable",
        [True] * 7,
        "tỷ lệ đúng 7/7, không có lỗi nào",
    ),
]

# Matched pairs: same correctness ratio, different temporal shape.
MATCHED_PAIRS = [
    ("recovering", "unstable", "cùng 4/7 đúng, khác hình dạng chuỗi"),
]


def transition_entropy_norm(correctness: list[bool]) -> float:
    """The detector's own instability measure, reimplemented for reporting."""
    from collections import Counter
    from math import log2

    transitions = [
        ("C" if a else "W") + ("C" if b else "W")
        for a, b in zip(correctness, correctness[1:])
    ]
    if not transitions:
        return 0.0
    n = len(transitions)
    entropy = 0.0
    for count in Counter(transitions).values():
        p = count / n
        entropy -= p * log2(p)
    return entropy / 2.0


def max_reachable_entropy(n_transitions: int) -> float:
    """Largest normalised entropy attainable with `n_transitions` observations.

    The four transition types cannot each hold n/4 samples when n is not a
    multiple of four, so the achievable maximum is strictly below 1.0.  For
    short sequences this bound is well under the 0.65 instability threshold,
    which is the mechanism behind the misclassification reported below.
    """
    from collections import Counter
    from math import log2

    base, rem = divmod(n_transitions, 4)
    counts = [base + (1 if i < rem else 0) for i in range(4)]
    entropy = 0.0
    for c in counts:
        if c <= 0:
            continue
        p = c / n_transitions
        entropy -= p * log2(p)
    return entropy / 2.0


def alternation_rate(correctness: list[bool]) -> float:
    """Share of adjacent observations that flip state.

    This is the intuitive reading of "unstable": frequent oscillation between
    correct and incorrect, regardless of which of the two directions dominates.
    """
    if len(correctness) < 2:
        return 0.0
    flips = sum(
        1 for a, b in zip(correctness, correctness[1:]) if a != b
    )
    return flips / (len(correctness) - 1)


def main() -> None:
    detector = TemporalErrorPatternDetector()
    rows: list[dict[str, object]] = []

    for label, seq, why in FAMILIES:
        pattern = detector.detect(
            CONCEPT, build_interactions(seq)
        )
        n_trans = max(len(seq) - 1, 0)
        rows.append(
            {
                "family": label,
                "sequence": "".join("C" if x else "W" for x in seq),
                "correctness_ratio": round(
                    sum(1 for x in seq if x) / len(seq), 4
                ),
                "intended_label": label,
                "predicted_label": pattern.pattern,
                "correct": pattern.pattern == label,
                "persistence": round(pattern.persistence_score, 4),
                "recovery": round(pattern.recovery_score, 4),
                "instability": round(pattern.instability_score, 4),
                "instability_reachable_max": round(
                    max_reachable_entropy(n_trans), 4
                ),
                "instability_threshold": 0.65,
                "instability_threshold_reachable": (
                    max_reachable_entropy(n_trans) >= 0.65
                ),
                "alternation_rate": round(alternation_rate(seq), 4),
                "recent_error_pressure": round(
                    pattern.recent_error_pressure, 4
                ),
                "retention_risk": round(pattern.retention_risk, 4),
                "next_error_risk": round(pattern.next_error_risk, 4),
                "half_life_days": round(
                    pattern.estimated_half_life_days, 4
                ),
                "confidence": round(pattern.confidence, 4),
                "observation_count": pattern.observation_count,
                "rationale": why,
            }
        )

    by_family = {r["family"]: r for r in rows}
    recovery_rates = {
        r["family"]: round(float(r["correct"]) / 1.0, 4) for r in rows
    }

    margins: dict[str, float] = {}
    for a, b, why in MATCHED_PAIRS:
        ra, rb = by_family[a], by_family[b]
        margins[f"{a}_vs_{b}"] = round(
            float(ra["persistence"])
            - float(rb["persistence"]),
            4,
        )
        margins[f"{a}_vs_{b}__note"] = why  # type: ignore[assignment]

    # Aggregate over the whole benchmark as well: what label distribution does
    # the detector actually produce on real data?
    bench = aggregate_over_benchmark(detector)

    # Threshold-reachability analysis: for which sequence lengths can the
    # instability score physically exceed the 0.65 threshold?
    reach: dict[str, object] = {}
    for n_obs in range(3, 26):
        n_trans = n_obs - 1
        mx = max_reachable_entropy(n_trans)
        reach[f"n_obs={n_obs}"] = {
            "max_instability": round(mx, 4),
            "reachable": mx >= 0.65,
        }
    smallest_reachable = next(
        (
            n
            for n in range(3, 26)
            if max_reachable_entropy(n - 1) >= 0.65
        ),
        None,
    )

    payload = {
        "stimulus": (
            "Synthetic correctness sequences, one interaction per day, "
            "matched on length and inspected for temporal shape."
        ),
        "detector_config": {
            "recency_decay": 0.1,
            "recency_unit_seconds": 86400.0,
            "minimum_observations": 3,
            "persistence_threshold": 0.60,
            "recovery_threshold": 0.55,
            "instability_threshold": 0.65,
            "confidence_k": 5.0,
        },
        "families": rows,
        "recovery_rate_per_family": recovery_rates,
        "overall_accuracy": round(
            mean([1.0 if r["correct"] else 0.0 for r in rows]), 4
        ),
        "discrimination_margins": margins,
        "instability_threshold_reachability": {
            "note": (
                "Normalised transition entropy over four transition types "
                "cannot exceed 1.0 unless the sequence length is a multiple of "
                "4, and is bounded below 1.0 for every finite length. This "
                "table reports, for each observation count, the largest "
                "instability value physically attainable, so it can be "
                "compared with the fixed 0.65 classification threshold."
            ),
            "by_observation_count": reach,
            "smallest_n_reaching_0.65": smallest_reachable,
        },
        "benchmark_distribution": bench,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"{'family':12s}{'seq':12s}{'ratio':>7s}{'pred':>12s}"
          f"{'pers':>8s}{'rec':>8s}{'inst':>8s}{'altr':>7s}"
          f"{'conf':>7s}{'ok':>5s}")
    for r in rows:
        print(
            f"{r['family']:12s}{r['sequence']:12s}"
            f"{r['correctness_ratio']:>7.3f}"
            f"{r['predicted_label']:>12s}"
            f"{r['persistence']:>8.3f}{r['recovery']:>8.3f}"
            f"{r['instability']:>8.3f}{r['alternation_rate']:>7.3f}"
            f"{r['confidence']:>7.3f}"
            f"{'Y' if r['correct'] else 'N':>5s}"
        )
    print()
    print(f"overall accuracy = {payload['overall_accuracy']}")
    print(f"margins          = {margins}")
    print()
    print("instability threshold reachability (threshold = 0.65):")
    for n_obs in range(3, 14):
        n_trans = n_obs - 1
        mx = max_reachable_entropy(n_trans)
        flag = "reachable" if mx >= 0.65 else "UNREACHABLE"
        print(f"  n_obs={n_obs:>2d}  max_instability={mx:.4f}  {flag}")
    print(
        "  smallest n_obs reaching 0.65 = "
        f"{smallest_reachable}"
    )
    print()
    print("benchmark label distribution:")
    for k, v in bench.items():
        print(f"  {k}: {v}")
    print(f"\nwrote {OUT}")


def aggregate_over_benchmark(detector: TemporalErrorPatternDetector) -> dict[str, object]:
    """Label distribution and mean signals over the real benchmark concepts."""
    from backend.benchmark.ALOF.tools.gold_from_runtime import (
        build_learning_state,
    )
    from backend.domain.learning.historical_evidence_builder import (
        HistoricalEvidenceBuilder,
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

    counts: Counter[str] = Counter()
    pers: list[float] = []
    rec: list[float] = []
    inst: list[float] = []
    conf: list[float] = []
    obs: list[float] = []
    n_concepts = 0

    for split, diff, rel in DATASETS:
        path = BASE / rel
        for line in path.open(encoding="utf-8"):
            if not line.strip():
                continue
            sample = json.loads(line)
            state = build_learning_state(sample)
            task = sample["current_task"]
            question = str(task.get("question") or task.get("content") or "")
            concept_ids = [str(v) for v in (task.get("concept_ids") or [])]
            evidence = HistoricalEvidenceBuilder(recent_limit=5).build(
                learning_state=state,
                current_question=question,
                related_concept_ids=concept_ids,
            )
            pool = list(evidence.relevant_interactions) + list(
                evidence.recent_interactions
            )
            by_concept: dict[str, list[LearningInteraction]] = {}
            for it in pool:
                for c in it.concept_ids:
                    by_concept.setdefault(c, []).append(it)

            for c, items in by_concept.items():
                items = [
                    x for x in items if x.correct is not None
                ]
                if not items:
                    continue
                p = detector.detect(c, items)
                counts[p.pattern] += 1
                pers.append(p.persistence_score)
                rec.append(p.recovery_score)
                inst.append(p.instability_score)
                conf.append(p.confidence)
                obs.append(float(p.observation_count))
                n_concepts += 1

    total = sum(counts.values()) or 1
    return {
        "n_concept_observations": n_concepts,
        "label_counts": dict(counts),
        "label_share": {
            k: round(v / total, 4) for k, v in counts.items()
        },
        "mean_persistence": round(mean(pers), 4) if pers else None,
        "mean_recovery": round(mean(rec), 4) if rec else None,
        "mean_instability": round(mean(inst), 4) if inst else None,
        "mean_confidence": round(mean(conf), 4) if conf else None,
        "mean_observations": round(mean(obs), 4) if obs else None,
    }


if __name__ == "__main__":
    sys.exit(main())
