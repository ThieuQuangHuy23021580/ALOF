"""Check consistency between stored dataset memory gold and the K=5 runtime gold.

Diagnostic only. Reports how many cases have stored top_k_interactions that
differ from what the deterministic K=5 selector produces today, and how the
K=5 selection scores against the stored gold.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.benchmark.ALOF.tools.gold_from_runtime import (  # noqa: E402
    compute_memory_gold,
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


def main() -> None:
    print(
        f"{'dataset':26s} {'n':>3s} {'goldlen':>8s} {'mismatch':>9s} "
        f"{'K5 exact':>9s} {'K5 F1':>7s} {'K8-in-gold?':>12s}"
    )
    tot_n = tot_mm = tot_exact = 0
    f1_sum = 0.0
    for split, diff, rel in DATASETS:
        path = BASE / rel
        n = mm = exact = 0
        gold_len = 0
        f1_sum_d = 0.0
        for line in path.open(encoding="utf-8"):
            if not line.strip():
                continue
            sample = json.loads(line)
            n += 1
            stored = list(
                ((sample.get("expected") or {}).get("memory") or {}).get(
                    "top_k_interactions"
                ) or []
            )
            gold_len = len(stored)
            fresh = compute_memory_gold(sample)["top_k_interactions"]
            if set(stored) != set(fresh):
                mm += 1
            gset, aset = set(stored), set(fresh)
            if gset == aset:
                exact += 1
            matched = gset & aset
            p = len(matched) / len(aset) if aset else 0.0
            r = len(matched) / len(gset) if gset else 0.0
            f1 = (2 * p * r / (p + r)) if (p + r) else 0.0
            f1_sum_d += f1
        tot_n += n
        tot_mm += mm
        tot_exact += exact
        f1_sum += f1_sum_d
        print(
            f"{split + '_' + diff:26s} {n:3d} {gold_len:8d} {mm:9d} "
            f"{exact:9d} {f1_sum_d / n:7.4f} {'yes' if gold_len > 5 else 'no':>12s}"
        )
    print("-" * 82)
    print(
        f"{'TOTAL':26s} {tot_n:3d} {'':8s} {tot_mm:9d} {tot_exact:9d} {f1_sum / tot_n:7.4f}"
    )


if __name__ == "__main__":
    main()
