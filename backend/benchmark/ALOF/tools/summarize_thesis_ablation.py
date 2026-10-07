"""Aggregate thesis_ablation.json into macro / weighted averages for the thesis tables."""
from __future__ import annotations

import json
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "backend" / "benchmark" / "ALOF" / "reports" / "thesis_ablation.json"

KEYS = [
    "mem_full_f1", "mem_recency_f1", "mem_concept_f1", "mem_lexical_f1", "mem_chatbot_f1",
    "mem_full_exact", "mem_recency_exact", "mem_concept_exact", "mem_lexical_exact", "mem_chatbot_exact",
    "diag_alof_concept", "diag_alof_level",
    "diag_chatbot_concept", "diag_chatbot_level",
    "diag_no_evidence_concept", "diag_no_evidence_level",
    "diag_no_temporal_concept", "diag_no_temporal_level",
    "str_alof_action", "str_alof_strategy", "str_alof_difficulty", "str_alof_focus_f1",
    "str_chatbot_action", "str_chatbot_strategy", "str_chatbot_difficulty", "str_chatbot_focus_f1",
    "str_no_evidence_action", "str_no_evidence_strategy", "str_no_evidence_difficulty", "str_no_evidence_focus_f1",
    "str_no_temporal_action", "str_no_temporal_strategy", "str_no_temporal_difficulty", "str_no_temporal_focus_f1",
]


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    rows = data["results"]
    total = sum(int(r["n"]) for r in rows)

    print("=== DATASET STATS ===")
    for r in data["datasets"]:
        print(r)

    print()
    print(f"=== AGGREGATES over {total} cases ===")
    print(f"{'metric':34s} {'macro':>8s} {'weighted':>9s}")
    for key in KEYS:
        vals = [r[key] for r in rows if key in r]
        macro = mean(vals)
        weighted = sum(r[key] * r["n"] for r in rows if key in r) / total
        print(f"{key:34s} {macro:8.4f} {weighted:9.4f}")


if __name__ == "__main__":
    main()
