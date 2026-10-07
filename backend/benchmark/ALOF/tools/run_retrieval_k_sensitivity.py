"""K-sensitivity of ALOF retrieval against the independent concept-overlap gold.

Chapter 3 argued that the value of K changes both the system output *and* the
reference set, so F1 is not comparable across values of K.  This script makes
that argument concrete: for K in {1,3,5,8,10,12} it reports the achieved F1 and
the analytically reachable ceiling of a perfect ranker under that same K.

The gap between achieved and ceiling is the part of the error caused by
ranking; the ceiling itself is the part forced by the budget.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.benchmark.ALOF.tools.run_retrieval_signal_ablation import (  # noqa: E402
    DATASETS,
    FULL_WEIGHTS,
    candidate_pool,
    independent_gold,
    ndcg,
    prf,
    select_with_weights,
)
from backend.infrastructure.prompts.context_builder import (  # noqa: E402
    ContextBuilder,
)

BASE = ROOT / "backend" / "benchmark" / "ALOF"
OUT = BASE / "reports" / "retrieval_k_sensitivity.json"

KS = [1, 3, 5, 8, 10, 12]


def ceiling_f1(gold_size: int, k: int) -> float:
    """F1 of a perfect ranker when the gold has `gold_size` items and K = k."""
    if gold_size <= 0:
        return 1.0
    return 2 * min(k, gold_size) / (k + gold_size)


def main() -> None:
    # cache pools and golds once; they do not depend on K
    cases: list[tuple[dict, list[dict], set[str], str, list[str]]] = []
    for split, diff, rel in DATASETS:
        path = BASE / rel
        for line in path.open(encoding="utf-8"):
            if not line.strip():
                continue
            sample = json.loads(line)
            question, concept_ids, records, _ = candidate_pool(sample)
            gold = independent_gold(sample, records)
            cases.append((sample, records, gold, question, concept_ids))

    rows: list[dict[str, object]] = []
    for k in KS:
        acc: dict[str, list[float]] = {}
        ceilings: list[float] = []
        budget_blocked: list[int] = []
        selected_sizes: list[float] = []
        for _, records, gold, question, concept_ids in cases:
            pred = select_with_weights(
                records,
                question,
                concept_ids,
                FULL_WEIGHTS,
                top_k=k,
                max_tokens=ContextBuilder.MEMORY_MAX_TOKENS,
            )
            p, r, f = prf(gold, pred)
            acc.setdefault("P", []).append(p)
            acc.setdefault("R", []).append(r)
            acc.setdefault("F1", []).append(f)
            acc.setdefault("nDCG", []).append(ndcg(gold, pred, k))
            acc.setdefault("exact", []).append(
                float(set(pred) == gold)
            )
            ceilings.append(ceiling_f1(len(gold), k))
            selected_sizes.append(len(pred))
            budget_blocked.append(1 if len(pred) < min(k, len(records)) else 0)

        row: dict[str, object] = {
            "k": k,
            "mean_selected_size": round(mean(selected_sizes), 4),
            "oracle_ceiling_F1": round(mean(ceilings), 4),
            "share_cases_token_blocked": round(
                mean([float(x) for x in budget_blocked]), 4
            ),
        }
        for m in ("P", "R", "F1", "nDCG", "exact"):
            row[m] = round(mean(acc[m]), 4)
        row["gap_to_ceiling_F1"] = round(
            float(row["oracle_ceiling_F1"]) - float(row["F1"]), 4
        )
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False))

    payload = {
        "gold": "concept-overlap relevant set (independent of ranking)",
        "max_tokens": ContextBuilder.MEMORY_MAX_TOKENS,
        "default_k": ContextBuilder.MEMORY_TOP_K,
        "note": (
            "The candidate pool is capped at 50 records and the token budget "
            "at 1200, so selected size saturates below K for large K."
        ),
        "total_cases": len(cases),
        "rows": rows,
    }
    OUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print()
    print(f"{'K':>3s}{'sel':>8s}{'P':>9s}{'R':>9s}{'F1':>9s}{'nDCG':>9s}"
          f"{'exact':>9s}{'ceiling':>10s}{'gap':>9s}{'blocked':>9s}")
    for r in rows:
        print(
            f"{r['k']:>3d}{r['mean_selected_size']:>8.2f}"
            f"{r['P']:>9.4f}{r['R']:>9.4f}{r['F1']:>9.4f}{r['nDCG']:>9.4f}"
            f"{r['exact']:>9.4f}{r['oracle_ceiling_F1']:>10.4f}"
            f"{r['gap_to_ceiling_F1']:>9.4f}"
            f"{r['share_cases_token_blocked']:>9.4f}"
        )
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
