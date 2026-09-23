from __future__ import annotations

import argparse
import json
from pathlib import Path

from backend.benchmark.ALOF.tools.gold_from_runtime import (
    compute_runtime_gold,
)


def process_file(path: Path, *, dry_run: bool) -> dict[str, int]:
    lines_out: list[str] = []
    stats = {"cases": 0, "changed": 0}

    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            sample = json.loads(line)
            stats["cases"] += 1

            gold = compute_runtime_gold(sample)
            expected = sample.setdefault("expected", {})
            old = {
                "memory": dict(expected.get("memory") or {}),
                "diagnosis": dict(expected.get("diagnosis") or {}),
                "strategy": dict(expected.get("strategy") or {}),
            }

            memory = expected.setdefault("memory", {})
            memory["relevant_interactions"] = gold["memory"][
                "relevant_interactions"
            ]
            memory["top_k_interactions"] = gold["memory"][
                "top_k_interactions"
            ]

            diagnosis = expected.setdefault("diagnosis", {})
            for key, value in gold["diagnosis"].items():
                diagnosis[key] = value

            strategy = expected.setdefault("strategy", {})
            for key, value in gold["strategy"].items():
                strategy[key] = value

            changed = (
                old["memory"].get("relevant_interactions")
                != memory.get("relevant_interactions")
                or old["memory"].get("top_k_interactions")
                != memory.get("top_k_interactions")
                or old["diagnosis"].get("concept")
                != diagnosis.get("concept")
                or old["diagnosis"].get("level")
                != diagnosis.get("level")
                or list(old["diagnosis"].get("weak_concepts") or [])
                != list(diagnosis.get("weak_concepts") or [])
                or old["strategy"].get("action")
                != strategy.get("action")
                or old["strategy"].get("strategy")
                != strategy.get("strategy")
                or old["strategy"].get("difficulty")
                != strategy.get("difficulty")
                or list(old["strategy"].get("focus_concepts") or [])
                != list(strategy.get("focus_concepts") or [])
            )

            if changed:
                stats["changed"] += 1
                print(
                    f"[{path.name}:{line_no}] {sample['case_id']} "
                    f"diag={diagnosis.get('level')} "
                    f"diff={strategy.get('difficulty')} "
                    f"action={strategy.get('action')} "
                    f"top_k={memory.get('top_k_interactions')}"
                )

            lines_out.append(
                json.dumps(sample, ensure_ascii=False, separators=(",", ":"))
            )

    if not dry_run:
        path.write_text("\n".join(lines_out) + "\n", encoding="utf-8")

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Regenerate ALOF memory/diagnosis/strategy gold from "
            "the deterministic AdaptiveLearningPipeline."
        )
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="JSONL dataset files or directories",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print changes without writing files",
    )
    args = parser.parse_args()

    files: list[Path] = []
    for raw in args.paths:
        p = Path(raw)
        if p.is_dir():
            files.extend(sorted(p.rglob("*.jsonl")))
        else:
            files.append(p)

    total = {"cases": 0, "changed": 0}
    for file_path in files:
        result = process_file(file_path, dry_run=args.dry_run)
        total["cases"] += result["cases"]
        total["changed"] += result["changed"]
        print(
            f"{file_path}: cases={result['cases']} "
            f"changed={result['changed']}"
        )

    print(
        f"Done. cases={total['cases']} changed={total['changed']} "
        f"dry_run={args.dry_run}"
    )


if __name__ == "__main__":
    main()
