"""Evaluate a candidate fix for the instability signal in ALOF.

Finding this script responds to
-------------------------------
`run_temporal_pattern_stats.py` shows that `TemporalErrorPatternDetector`
misclassifies three of four matched probe families.  Root cause is that the
instability score is the normalised entropy of the four transition types
`{CC, CW, WC, WW}`.

That quantity does not measure oscillation.  It measures how evenly the four
transition types are spread, which is maximised by a *block* structure and
minimised by *pure alternation*:

    CCCWWWW  -> {CC:2, CW:1, WW:3}  -> 3 types -> H_norm = 0.730
    CWCWCWC  -> {CW:3, WC:3}        -> 2 types -> H_norm = 0.500

So a learner who is stable for days then wrong for days scores *higher*
instability than a learner who alternates on every single attempt.  Because
`_classify` tests instability first, block sequences are labelled `unstable`
and pure alternation is never labelled `unstable` at all.

Candidate fix
-------------
Replace the entropy signal with an alternation rate:

    S_inst = (# adjacent observations that flip) / (n - 1)

which is 1.0 for pure alternation, near 0.0 for a block, and is exactly the
quantity the label `unstable` is meant to denote.  This script measures what
that change would do, on two test sets:

  1. the matched synthetic probe families (discrimination);
  2. the real benchmark concepts (label distribution shift).

It does not modify the detector.  It reports numbers so the change can be
decided on evidence.
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
OUT = BASE / "reports" / "temporal_instability_fix_evaluation.json"

INSTABILITY_THRESHOLD = 0.65
PERSISTENCE_THRESHOLD = 0.60
RECOVERY_THRESHOLD = 0.55
MIN_OBSERVATIONS = 3
CONCEPT = "c"

PROBES: list[tuple[str, str]] = [
    ("persistent", "CCCWWWW"),
    ("recovering", "WWWCCCC"),
    ("unstable", "CWCWCWC"),
    ("stable", "CCCCCCC"),
]


def to_booleans(seq: str) -> list[bool]:
    return [c == "C" for c in seq]


def build(seq: str) -> list[LearningInteraction]:
    start = datetime(2026, 1, 1, tzinfo=UTC)
    return [
        LearningInteraction(
            id=f"{CONCEPT}_{i}",
            learner_id="p",
            question_id=f"q{i}",
            question="x",
            answer="a",
            correct=ok,
            concept_ids=[CONCEPT],
            timestamp=start + timedelta(days=i),
        )
        for i, ok in enumerate(to_booleans(seq))
    ]


def alternation_rate(correctness: list[bool]) -> float:
    if len(correctness) < 2:
        return 0.0
    flips = sum(1 for a, b in zip(correctness, correctness[1:]) if a != b)
    return flips / (len(correctness) - 1)


def entropy_instability(correctness: list[bool]) -> float:
    from math import log2

    trans = [
        ("C" if a else "W") + ("C" if b else "W")
        for a, b in zip(correctness, correctness[1:])
    ]
    if not trans:
        return 0.0
    n = len(trans)
    h = 0.0
    for c in Counter(trans).values():
        p = c / n
        h -= p * log2(p)
    return min(1.0, h / 2.0)


def classify(
    *,
    n_obs: int,
    persistence: float,
    recovery: float,
    instability: float,
    recent_pressure: float,
) -> str:
    """Same precedence as TemporalErrorPatternDetector._classify."""
    if n_obs < MIN_OBSERVATIONS:
        return "stable"
    if instability >= INSTABILITY_THRESHOLD:
        return "unstable"
    if (
        persistence >= PERSISTENCE_THRESHOLD
        and recent_pressure >= PERSISTENCE_THRESHOLD
    ):
        return "persistent"
    if recovery >= RECOVERY_THRESHOLD and recovery > persistence:
        return "recovering"
    return "stable"


def evaluate_probe() -> dict[str, object]:
    det = TemporalErrorPatternDetector()
    rows: list[dict[str, object]] = []
    for label, seq in PROBES:
        p = det.detect(CONCEPT, build(seq))
        corr = to_booleans(seq)
        alt = alternation_rate(corr)
        ent_val = entropy_instability(corr)
        fixed = classify(
            n_obs=p.observation_count,
            persistence=p.persistence_score,
            recovery=p.recovery_score,
            instability=alt,
            recent_pressure=p.recent_error_pressure,
        )
        rows.append(
            {
                "intended": label,
                "sequence": seq,
                "entropy_instability": round(ent_val, 4),
                "alternation": round(alt, 4),
                "persistence": round(p.persistence_score, 4),
                "recovery": round(p.recovery_score, 4),
                "recent_error_pressure": round(p.recent_error_pressure, 4),
                "current_label": p.pattern,
                "fixed_label": fixed,
                "current_ok": p.pattern == label,
                "fixed_ok": fixed == label,
            }
        )
    return {
        "rows": rows,
        "current_accuracy": round(
            mean([1.0 if r["current_ok"] else 0.0 for r in rows]), 4
        ),
        "fixed_accuracy": round(
            mean([1.0 if r["fixed_ok"] else 0.0 for r in rows]), 4
        ),
    }


def evaluate_benchmark() -> dict[str, object]:
    from backend.benchmark.ALOF.tools.gold_from_runtime import (
        build_learning_state,
    )
    from backend.domain.learning.historical_evidence_builder import (
        HistoricalEvidenceBuilder,
    )

    DATASETS = [
        ("data/long_context/adaptive_learning_vi_longcontext_easy.jsonl"),
        ("data/long_context/adaptive_learning_vi_longcontext_medium.jsonl"),
        ("data/multi_concept/adaptive_learning_vi_multiconcept_easy.jsonl"),
        ("data/multi_concept/adaptive_learning_vi_multiconcept_medium.jsonl"),
        ("data/multi_concept/adaptive_learning_vi_multiconcept_hard.jsonl"),
        ("data/strategy/adaptive_learning_vi_strategy_easy.jsonl"),
        ("data/strategy/adaptive_learning_vi_strategy_medium.jsonl"),
        ("data/strategy/adaptive_learning_vi_strategy_hard.jsonl"),
    ]

    det = TemporalErrorPatternDetector()
    current: Counter[str] = Counter()
    fixed: Counter[str] = Counter()
    changed: list[dict[str, object]] = []
    flips = 0
    total = 0

    for rel in DATASETS:
        for line in (BASE / rel).open(encoding="utf-8"):
            if not line.strip():
                continue
            sample = json.loads(line)
            state = build_learning_state(sample)
            task = sample["current_task"]
            question = str(task.get("question") or task.get("content") or "")
            concept_ids = [str(v) for v in (task.get("concept_ids") or [])]
            ev = HistoricalEvidenceBuilder(recent_limit=5).build(
                learning_state=state,
                current_question=question,
                related_concept_ids=concept_ids,
            )
            pool = list(ev.relevant_interactions) + list(
                ev.recent_interactions
            )
            by_concept: dict[str, list[LearningInteraction]] = {}
            for it in pool:
                for c in it.concept_ids:
                    by_concept.setdefault(c, []).append(it)

            for cid, items in by_concept.items():
                items = [x for x in items if x.correct is not None]
                if not items:
                    continue
                p = det.detect(cid, items)
                corr = [x.correct for x in items]
                alt = alternation_rate(corr)
                new_label = classify(
                    n_obs=p.observation_count,
                    persistence=p.persistence_score,
                    recovery=p.recovery_score,
                    instability=alt,
                    recent_pressure=p.recent_error_pressure,
                )
                current[p.pattern] += 1
                fixed[new_label] += 1
                total += 1
                if new_label != p.pattern:
                    flips += 1
                    if len(changed) < 20:
                        changed.append(
                            {
                                "concept": cid,
                                "n_obs": p.observation_count,
                                "sequence": "".join(
                                    "C" if x else "W" for x in corr
                                ),
                                "entropy_instability": round(
                                    entropy_instability(corr), 4
                                ),
                                "alternation": round(alt, 4),
                                "current": p.pattern,
                                "fixed": new_label,
                            }
                        )

    n = total or 1
    return {
        "n_concept_observations": total,
        "current_counts": dict(current),
        "current_share": {
            k: round(v / n, 4) for k, v in current.items()
        },
        "fixed_counts": dict(fixed),
        "fixed_share": {k: round(v / n, 4) for k, v in fixed.items()},
        "n_labels_changed": flips,
        "share_labels_changed": round(flips / n, 4),
        "examples": changed,
    }


def main() -> None:
    probe = evaluate_probe()
    bench = evaluate_benchmark()

    payload = {
        "candidate_fix": (
            "Replace the normalised transition-entropy instability signal "
            "with the alternation rate (share of adjacent observations that "
            "flip), keeping the same 0.65 threshold and the same precedence "
            "order in _classify."
        ),
        "root_cause": (
            "Normalised entropy over {CC,CW,WC,WW} measures how evenly the "
            "four transition types are spread, not how often the learner "
            "flips. A block sequence uses three types with skewed counts and "
            "scores ~0.73, while pure alternation uses only two types and "
            "scores exactly 0.50. Because _classify tests instability first, "
            "block sequences are labelled 'unstable' and pure alternation is "
            "never labelled 'unstable'."
        ),
        "probe": probe,
        "benchmark": bench,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("PROBE FAMILIES")
    print(
        f"{'intended':12s}{'seq':10s}{'entropy':>9s}{'altern':>8s}"
        f"{'current':>12s}{'fixed':>12s}"
    )
    for r in probe["rows"]:
        print(
            f"{r['intended']:12s}{r['sequence']:10s}"
            f"{r['entropy_instability']:>9.3f}{r['alternation']:>8.3f}"
            f"{r['current_label']:>12s}{r['fixed_label']:>12s}"
        )
    print()
    print(f"probe accuracy: current={probe['current_accuracy']} "
          f"fixed={probe['fixed_accuracy']}")
    print()
    print("BENCHMARK LABEL DISTRIBUTION")
    print(f"  n = {bench['n_concept_observations']}")
    print(f"  current: {bench['current_counts']}")
    print(f"  fixed:   {bench['fixed_counts']}")
    print(
        f"  labels changed: {bench['n_labels_changed']} "
        f"({bench['share_labels_changed']:.2%})"
    )
    for e in bench["examples"][:8]:
        print(
            f"    {e['sequence']:<12s} n={e['n_obs']} "
            f"ent={e['entropy_instability']:.3f} alt={e['alternation']:.3f} "
            f"{e['current']} -> {e['fixed']}"
        )
    print()
    print(f"wrote {OUT}")


if __name__ == "__main__":
    sys.exit(main())
