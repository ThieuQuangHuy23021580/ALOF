"""Aggregate topK token-usage sidecars for the experiments chapter."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TOKENS = ROOT / "backend" / "benchmark" / "ALOF" / "results" / "topK_8"


def main() -> None:
    files = sorted(TOKENS.glob("*_tokens.json"))
    print(
        f"{'dataset':28s} {'exec':>5s} {'ok':>4s} {'skip':>5s} {'fail':>5s} "
        f"{'in_tok':>9s} {'out_tok':>8s} {'calls':>6s} {'sec':>9s}"
    )
    ti = to = tc = 0
    dur = 0.0
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        a = d["aggregate_tokens"]
        name = f.stem.replace("results_", "").replace("_tokens", "")
        print(
            f"{name:28s} {d['executed_cases']:5d} {d['success_cases']:4d} "
            f"{d['skipped_cases']:5d} {d['failed_cases']:5d} "
            f"{a['input_tokens']:9d} {a['output_tokens']:8d} "
            f"{a['call_count']:6d} {a['duration_seconds']:9.0f}"
        )
        ti += a["input_tokens"]
        to += a["output_tokens"]
        tc += a["call_count"]
        dur += a["duration_seconds"]
    print("-" * 90)
    print(
        f"TOTAL in={ti} out={to} total={ti + to} calls={tc} "
        f"duration={dur:.0f}s ({dur / 3600:.2f} h)"
    )
    if tc:
        print(f"mean input/call  = {ti / tc:.0f}")
        print(f"mean output/call = {to / tc:.0f}")


if __name__ == "__main__":
    main()
