from __future__ import annotations

import argparse
import json
from pathlib import Path

from backend.benchmark.ALOF.tools.gold_from_runtime import (
    compute_memory_gold,
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

            memory_gold = compute_memory_gold(sample)
            expected = sample.setdefault("expected", {})
            memory = expected.setdefault("memory", {})

            old_relevant = list(memory.get("relevant_interactions") or [])
            old_top_k = list(memory.get("top_k_interactions") or [])

            memory["relevant_interactions"] = memory_gold[
                "relevant_interactions"
            ]
            memory["top_k_interactions"] = memory_gold["top_k_interactions"]

            if (
                old_relevant != memory["relevant_interactions"]
                or old_top_k != memory["top_k_interactions"]
            ):
                stats["changed"] += 1
                print(
                    f"[{path.name}:{line_no}] {sample['case_id']} "
                    f"top_k={memory['top_k_interactions']}"
                )

            lines_out.append(
                json.dumps(sample, ensure_ascii=False, separators=(",", ":"))
            )

    if not dry_run:
        path.write_text("\n".join(lines_out) + "\n", encoding="utf-8")

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Regenerate ALOF memory gold labels."
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
        f"Done. cases={total['cases']} changed={total['changed']} "
        f"dry_run={args.dry_run}"
    )


if __name__ == "__main__":
    main()
