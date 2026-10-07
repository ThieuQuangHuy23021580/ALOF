"""Compute the oracle ceiling of retrieval under ALOF's own budget constraints.

Why this matters
----------------
The reported F1 of every configuration is capped by two *constraints* that are
independent of ranking quality:

  * a fixed budget K (ContextBuilder.MEMORY_TOP_K), and
  * a token budget (ContextBuilder.MEMORY_MAX_TOKENS).

If the concept-overlap gold for a case has |E*| < K, the selector is forced to
add non-relevant records to reach K, and precision is capped below 1.  If
|E*| > K, recall is capped at K/|E*|.  Reporting raw F1 without this ceiling
makes a good ranker look mediocre and a perfect ranker look merely adequate.

This script measures the ceiling directly: it keeps the candidate pool, the
token estimator and the budget arithmetic of EvidenceSelector unchanged, and
simply forces the sort to put gold records first.  The result is the best F1 /
nDCG any deterministic ranker can reach on the same gold under the same
constraints.  The gap between ALOF and this ceiling is the part of the error
that is genuinely attributable to ranking, not to the budget.
"""
from __future__ import annotations

import json
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
)
from backend.benchmark.ALOF.tools.run_retrieval_signal_ablation import (  # noqa: E402
    DATASETS,
    FULL_WEIGHTS,
    independent_gold,
    candidate_pool,
    ndcg,
    prf,
    select_with_weights,
)
from backend.domain.learning.historical_evidence_builder import (  # noqa: E402
    HistoricalEvidenceBuilder,
)
from backend.infrastructure.prompts.context_builder import (  # noqa: E402
    ContextBuilder,
)

BASE = ROOT / "backend" / "benchmark" / "ALOF"
OUT = BASE / "reports" / "retrieval_oracle_ceiling.json"


def oracle_select(
    records: list[dict],
    gold: set[str],
    top_k: int = ContextBuilder.MEMORY_TOP_K,
    max_tokens: int = ContextBuilder.MEMORY_MAX_TOKENS,
) -> list[str]:
    """Same budget arithmetic as EvidenceSelector, but gold records first.

    This is the best any deterministic ranker can do on this gold under this
    budget, because the candidate pool, the token estimator, the de-duplication
    and the budget arithmetic are all left untouched; only the sort order of the
    gold block is forced to the front.
    """
    gold_block = [r for r in records if str(r.get("question_id")) in gold]
    rest = [r for r in records if str(r.get("question_id")) not in gold]
    gold_block.sort(key=lambda r: str(r.get("timestamp") or ""), reverse=True)
    rest.sort(key=lambda r: str(r.get("timestamp") or ""), reverse=True)

    selected: list[dict] = []
    keys: set[str] = set()
    used = 0
    for rec in gold_block + rest:
        if len(selected) >= top_k:
            break
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


def budget_capped_f1(gold_size: float, k: int) -> float:
    """F1 of a perfect ranker when the gold size is constant at `gold_size`.

    Only valid when the pool can actually supply k distinct records; callers must
    additionally cap by the reachable set size.
    """
    if gold_size <= 0:
        return 1.0
    reach = min(k, gold_size) if gold_size <= k else k
    return 2 * reach / (k + gold_size)


def main() -> None:
    per_ds: list[dict[str, object]] = []
    per_case_gap: list[float] = []
    ks = [int(x) for x in sys.argv[1:]] or [ContextBuilder.MEMORY_TOP_K]

    for split, diff, rel in DATASETS:
        path = BASE / rel
        acc: dict[str, list[float]] = {}
        gold_sizes: list[int] = []
        gaps: list[float] = []

        for line in path.open(encoding="utf-8"):
            if not line.strip():
                continue
            sample = json.loads(line)
            question, concept_ids, records, _ = candidate_pool(sample)
            gold = independent_gold(sample, records)
            gold_sizes.append(len(gold))

            for k in ks:
                pred = select_with_weights(
                    records, question, concept_ids, FULL_WEIGHTS, top_k=k
                )
                _, _, f_alof = prf(gold, pred)
                n_alof = ndcg(gold, pred, k)

                orc = oracle_select(records, gold, top_k=k)
                _, _, f_orc = prf(gold, orc)
                n_orc = ndcg(gold, orc, k)

                gaps.append(f_orc - f_alof)
                acc.setdefault(f"K{k}__alof_F1", []).append(f_alof)
                acc.setdefault(f"K{k}__alof_nDCG", []).append(n_alof)
                acc.setdefault(f"K{k}__oracle_F1", []).append(f_orc)
                acc.setdefault(f"K{k}__oracle_nDCG", []).append(n_orc)

        row: dict[str, object] = {
            "split": split,
            "difficulty": diff,
            "n": len(gold_sizes),
            "mean_gold_size": round(mean(gold_sizes), 4),
        }
        for key, vals in acc.items():
            row[key] = round(mean(vals), 4)
        per_ds.append(row)
        per_case_gap.extend(gaps)
        print(json.dumps(row, ensure_ascii=False))

    macro = {
        f"K{k}": {
            "alof_F1": round(
                mean([float(r[f"K{k}__alof_F1"]) for r in per_ds]), 4
            ),
            "oracle_F1": round(
                mean([float(r[f"K{k}__oracle_F1"]) for r in per_ds]), 4
            ),
            "alof_nDCG": round(
                mean([float(r[f"K{k}__alof_nDCG"]) for r in per_ds]), 4
            ),
            "oracle_nDCG": round(
                mean([float(r[f"K{k}__oracle_nDCG"]) for r in per_ds]), 4
            ),
        }
        for k in ks
    }
    for k in ks:
        a = macro[f"K{k}"]["alof_F1"]
        o = macro[f"K{k}"]["oracle_F1"]
        macro[f"K{k}"]["gap_F1"] = round(o - a, 4)
        macro[f"K{k}"]["share_of_ceiling"] = round(a / o, 4) if o else None

    payload = {
        "ks": ks,
        "max_tokens": ContextBuilder.MEMORY_MAX_TOKENS,
        "note": (
            "Oracle keeps ALOF's candidate pool, token estimator, de-duplication "
            "and budget arithmetic; it only forces gold records to sort first. "
            "The achieved/ceiling comparison is therefore budget-aware, unlike a "
            "closed-form ceiling that ignores pool exhaustion."
        ),
        "macro": macro,
        "per_case": {
            "n": len(per_case_gap),
            "mean_gap": round(mean(per_case_gap), 4),
            "max_gap": round(max(per_case_gap), 4),
            "min_gap": round(min(per_case_gap), 4),
            "share_cases_at_ceiling": round(
                sum(1 for g in per_case_gap if g < 1e-9) / len(per_case_gap), 4
            ),
        },
        "per_dataset": per_ds,
    }
    OUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print()
    print(f"{'K':>3s}{'ALOF F1':>10s}{'oracle F1':>11s}"
          f"{'gap':>9s}{'share':>9s}{'ALOF nDCG':>11s}{'oracle nDCG':>13s}")
    for k in ks:
        m = macro[f"K{k}"]
        print(
            f"{k:>3d}{m['alof_F1']:>10.4f}{m['oracle_F1']:>11.4f}"
            f"{m['gap_F1']:>9.4f}{m['share_of_ceiling']:>9.4f}"
            f"{m['alof_nDCG']:>11.4f}{m['oracle_nDCG']:>13.4f}"
        )
    print()
    print(f"per-case gap: {payload['per_case']}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
