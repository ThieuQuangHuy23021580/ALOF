"""Aggregate per-dataset topK_8 evaluator reports into one macro table.

Used for the Top-K sensitivity table in the experiments chapter.
"""
from __future__ import annotations

import json
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[4]
REPORTS = ROOT / "backend" / "benchmark" / "ALOF" / "reports" / "topK_8"


def main() -> None:
    files = sorted(REPORTS.glob("report_*.json"))
    print(f"{'dataset':32s} {'exec':>6s} {'memF1':>7s} {'diag':>6s} {'strat':>6s} {'sem':>6s}")
    acc: dict[str, list[float]] = {}
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        name = f.stem.replace("report_", "")
        row = {
            "exec": d["execution_success_rate"],
            "memF1": d["memory"]["mean_f1"],
            "memPass": d["memory"]["pass_rate"],
            "diag": d["diagnosis"]["pass_rate"],
            "strat": d["strategy"]["pass_rate"],
            "sem": d["semantic_pass_rate"],
        }
        for k, v in row.items():
            acc.setdefault(k, []).append(v)
        print(
            f"{name:32s} {row['exec']:6.2f} {row['memF1']:7.4f} "
            f"{row['diag']:6.2f} {row['strat']:6.2f} {row['sem']:6.2f}"
        )
    print("-" * 70)
    print(
        f"{'MACRO (8 sets)':32s} {mean(acc['exec']):6.2f} {mean(acc['memF1']):7.4f} "
        f"{mean(acc['diag']):6.2f} {mean(acc['strat']):6.2f} {mean(acc['sem']):6.2f}"
    )


if __name__ == "__main__":
    main()
