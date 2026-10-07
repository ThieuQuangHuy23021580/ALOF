"""Aggregate the offline signal-level retrieval ablation into a macro table.

Reads reports/retrieval_signal_ablation.json (produced by
run_retrieval_signal_ablation.py) and prints/writes the macro averages used in
the experiments chapter of the thesis.
"""
from __future__ import annotations

import json
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "backend" / "benchmark" / "ALOF"
IN_PATH = BASE / "reports" / "retrieval_signal_ablation.json"
OUT_PATH = BASE / "reports" / "retrieval_signal_ablation_summary.json"

# (label shown in the thesis, key in the raw report)
CONFIGS: list[tuple[str, str, str]] = [
    # label, key, kind
    ("ALOF (đa tín hiệu)", "ALOF-full", "ablation"),
    ("w/o concept", "w/o-concept", "ablation"),
    ("w/o error", "w/o-error", "ablation"),
    ("w/o recency", "w/o-recency", "ablation"),
    ("w/o semantic (lexical)", "w/o-semantic", "ablation"),
    ("w/o date", "w/o-date", "ablation"),
    ("recency-only", "recency-only", "single"),
    ("concept-only", "concept-only", "ablation"),
    ("single lexical", "lexical-only", "single"),
    ("recency baseline (full history)", "recency-baseline", "baseline"),
]

METRICS = ["P", "R", "F1", "nDCG", "exact"]


def main() -> None:
    data = json.loads(IN_PATH.read_text(encoding="utf-8"))
    rows = data["datasets"]
    n_cases = sum(int(r["n"]) for r in rows)

    out: dict[str, object] = {
        "k": data["metric_definitions"]["k"],
        "gold": data["metric_definitions"]["gold"],
        "gold_definition_note": data["metric_definitions"]["note"],
        "total_cases": n_cases,
        "total_elapsed_seconds": None,
        "sanity_check": data["sanity_full_vs_evidence_selector"],
    }

    per_config: list[dict[str, object]] = []
    for label, key, kind in CONFIGS:
        row: dict[str, object] = {"label": label, "key": key, "kind": kind}
        for metric in METRICS:
            vals = [float(r[f"{key}__{metric}"]) for r in rows]
            row[metric] = round(mean(vals), 4)
        per_config.append(row)
    out["macro"] = per_config

    # Per-dataset F1 for the three baselines + full ALOF.
    per_dataset: list[dict[str, object]] = []
    for r in rows:
        per_dataset.append(
            {
                "split": r["split"],
                "difficulty": r["difficulty"],
                "n": r["n"],
                "mean_gold_size": r["mean_gold_size"],
                "ALOF-full__F1": r["ALOF-full__F1"],
                "recency-only__F1": r["recency-only__F1"],
                "concept-only__F1": r["concept-only__F1"],
                "lexical-only__F1": r["lexical-only__F1"],
            }
        )
    out["per_dataset"] = {
        "split": per_dataset,
        "note": (
            "Gold is the concept-overlap relevant set, independent of the "
            "ranking function. K = 5."
        ),
    }

    out_path = OUT_PATH
    out_path.write_text(
        json.dumps(out, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"wrote {out_path}")

    # Console summary
    header = f"{'config':32s}" + "".join(f"{m:>9s}" for m in METRICS)
    print(header)
    print("-" * len(header))
    for row in per_config:
        line = f"{str(row['label']):32s}"
        for m in METRICS:
            line += f"{float(row[m]):9.4f}"
        print(line)
    print()
    print(f"{'per-dataset F1':32s}{'gold':>9s}{'ALOF':>9s}{'recency':>9s}{'concept':>9s}{'lexical':>9s}")
    for r in per_dataset:
        print(
            f"{r['split'] + '/' + r['difficulty']:32s}"
            f"{r['mean_gold_size']:9.2f}"
            f"{float(r['ALOF-full__F1']):9.4f}"
            f"{float(r['recency-only__F1']):9.4f}"
            f"{float(r['concept-only__F1']):9.4f}"
            f"{float(r['lexical-only__F1']):9.4f}"
        )
    print()
    print(f"sanity: {data['sanity_full_vs_evidence_selector']}")
    print(f"total cases: {n_cases}")


if __name__ == "__main__":
    main()
