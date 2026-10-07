"""
Phân tích token usage từ JSONL benchmark kết quả.

Usage:
    python -m backend.tools.analyze_token_usage \
        --results backend/benchmark/ALOF/results/results_strategy_easy.jsonl

In ra:
    - Tổng input/output/total tokens
    - Phân bố theo stage (router, planner, runtime, ...)
    - Top-N case tốn token nhất
    - Trung bình / median / percentile
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path


def load_results(path: Path) -> list[dict]:
    results = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            results.append(obj)
    return results


def per_case_totals(results: list[dict]) -> list[tuple[str, int]]:
    out = []
    for r in results:
        usage = r.get("token_usage", {}) or {}
        out.append(
            (
                str(r.get("case_id", "?")),
                int(usage.get("total_tokens", 0)),
            )
        )
    return out


def per_stage_totals(results: list[dict]) -> dict[str, dict[str, int]]:
    agg: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "call_count": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }
    )
    for r in results:
        usage = r.get("token_usage", {}) or {}
        for stage, entry in (usage.get("per_stage") or {}).items():
            agg[stage]["call_count"] += entry.get("call_count", 0)
            agg[stage]["input_tokens"] += entry.get("input_tokens", 0)
            agg[stage]["output_tokens"] += entry.get("output_tokens", 0)
            agg[stage]["total_tokens"] += entry.get("total_tokens", 0)
    return dict(agg)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze token consumption from ALOF benchmark results."
    )
    parser.add_argument(
        "--results",
        required=True,
        help="Path to the results JSONL file.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Number of top-N expensive cases to show.",
    )
    args = parser.parse_args()

    path = Path(args.results)
    if not path.exists():
        print(f"[ERROR] Results file not found: {path}", file=sys.stderr)
        sys.exit(1)

    results = load_results(path)
    if not results:
        print("[ERROR] No valid records in results.", file=sys.stderr)
        sys.exit(1)

    print("=" * 60)
    print(f"Token usage analysis: {path}")
    print(f"Total cases loaded: {len(results)}")
    print("=" * 60)

    totals = per_case_totals(results)
    total_tokens = sum(t for _, t in totals)
    input_tokens_total = sum(
        (r.get("token_usage", {}) or {}).get("input_tokens", 0)
        for r in results
    )
    output_tokens_total = sum(
        (r.get("token_usage", {}) or {}).get("output_tokens", 0)
        for r in results
    )
    calls_total = sum(
        (r.get("token_usage", {}) or {}).get("call_count", 0)
        for r in results
    )

    print()
    print("AGGREGATE")
    print("-" * 60)
    print(f"  LLM calls      : {calls_total}")
    print(f"  Input tokens   : {input_tokens_total:,}")
    print(f"  Output tokens  : {output_tokens_total:,}")
    print(f"  Total tokens   : {total_tokens:,}")
    if results:
        per_case_avg = total_tokens / len(results)
        print(f"  Per-case avg   : {per_case_avg:,.1f} tokens")

    # Distribution statistics
    values = [t for _, t in totals if t > 0]
    if values:
        print()
        print("DISTRIBUTION (non-zero cases)")
        print("-" * 60)
        print(f"  N         : {len(values)}")
        print(f"  Min       : {min(values):,} tokens")
        print(f"  Max       : {max(values):,} tokens")
        print(f"  Median    : {statistics.median(values):,.0f} tokens")
        print(f"  Mean      : {statistics.mean(values):,.1f} tokens")
        if len(values) >= 4:
            p90 = statistics.quantiles(values, n=10)[8]
            p95 = statistics.quantiles(values, n=20)[18]
            print(f"  P90       : {p90:,.0f} tokens")
            print(f"  P95       : {p95:,.0f} tokens")

    # Per-stage breakdown
    stages = per_stage_totals(results)
    if stages:
        print()
        print("PER STAGE")
        print("-" * 60)
        print(
            f"  {'stage':<22} {'calls':>6} {'in':>10} "
            f"{'out':>10} {'total':>11}"
        )
        for stage, entry in sorted(
            stages.items(),
            key=lambda x: x[1]["total_tokens"],
            reverse=True,
        ):
            print(
                f"  {stage:<22} "
                f"{entry['call_count']:>6} "
                f"{entry['input_tokens']:>10,} "
                f"{entry['output_tokens']:>10,} "
                f"{entry['total_tokens']:>11,}"
            )

    # Top-N most expensive cases
    top = sorted(totals, key=lambda x: x[1], reverse=True)[: args.top]
    if top:
        print()
        print(f"TOP {args.top} MOST EXPENSIVE CASES")
        print("-" * 60)
        for case_id, tok in top:
            print(f"  {case_id:<24} {tok:>10,} tokens")

    # Zero-token cases
    zero_count = sum(1 for _, t in totals if t == 0)
    if zero_count:
        print()
        print(
            f"NOTE: {zero_count} case(s) recorded 0 tokens "
            "(either failed or had no LLM call)."
        )

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()