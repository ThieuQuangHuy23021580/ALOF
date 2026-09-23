from __future__ import annotations

import json
from pathlib import Path

from backend.benchmark.ALOF.tools.gold_from_runtime import select_memory


DATASETS: list[tuple[str, str]] = [
    (
        "backend/benchmark/ALOF/data/long_context/adaptive_learning_vi_longcontext_easy.jsonl",
        "backend/benchmark/ALOF/results/results_longcontext_easy.jsonl",
    ),
    (
        "backend/benchmark/ALOF/data/long_context/adaptive_learning_vi_longcontext_medium.jsonl",
        "backend/benchmark/ALOF/results/results_longcontext_medium.jsonl",
    ),
    (
        "backend/benchmark/ALOF/data/multi_concept/adaptive_learning_vi_multiconcept_easy.jsonl",
        "backend/benchmark/ALOF/results/results_multiconcept_easy.jsonl",
    ),
    (
        "backend/benchmark/ALOF/data/multi_concept/adaptive_learning_vi_multiconcept_medium.jsonl",
        "backend/benchmark/ALOF/results/results_multiconcept_medium.jsonl",
    ),
    (
        "backend/benchmark/ALOF/data/multi_concept/adaptive_learning_vi_multiconcept_hard.jsonl",
        "backend/benchmark/ALOF/results/results_multiconcept_hard.jsonl",
    ),
    (
        "backend/benchmark/ALOF/data/strategy/adaptive_learning_vi_strategy_easy.jsonl",
        "backend/benchmark/ALOF/results/results_strategy_easy.jsonl",
    ),
    (
        "backend/benchmark/ALOF/data/strategy/adaptive_learning_vi_strategy_medium.jsonl",
        "backend/benchmark/ALOF/results/results_strategy_medium.jsonl",
    ),
    (
        "backend/benchmark/ALOF/data/strategy/adaptive_learning_vi_strategy_hard.jsonl",
        "backend/benchmark/ALOF/results/results_strategy_hard.jsonl",
    ),
]


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(
            json.dumps(
                row,
                ensure_ascii=False,
                separators=(",", ":"),
                default=str,
            )
            for row in rows
        )
        + "\n",
        encoding="utf-8",
    )


def patch_results(dataset_path: Path, results_path: Path) -> dict[str, int]:
    samples = {
        str(sample["case_id"]): sample
        for sample in load_jsonl(dataset_path)
    }
    results = load_jsonl(results_path)
    lengths: list[int] = []
    updated = 0

    for row in results:
        case_id = str(row.get("case_id") or "")
        sample = samples.get(case_id)
        if sample is None:
            continue

        selection = select_memory(sample)
        retrieval = list(selection["history"]) + list(
            selection["related_history"]
        )
        lengths.append(len(retrieval))

        metadata = row.get("runtime_metadata")
        if not isinstance(metadata, dict):
            metadata = {}
            row["runtime_metadata"] = metadata

        metadata["memory_retrieval"] = retrieval
        stats = selection.get("stats") or {}
        metadata["memory_selection_debug"] = stats.get("debug", {})
        updated += 1

    write_jsonl(results_path, results)

    return {
        "updated": updated,
        "min_k": min(lengths) if lengths else 0,
        "max_k": max(lengths) if lengths else 0,
        "mean_k": (
            round(sum(lengths) / len(lengths), 2) if lengths else 0
        ),
        "lt_10": sum(1 for n in lengths if n < 10),
        "eq_10": sum(1 for n in lengths if n == 10),
    }


def main() -> None:
    root = Path(".")
    for dataset, results in DATASETS:
        stats = patch_results(root / dataset, root / results)
        print(
            f"{Path(results).name}: updated={stats['updated']} "
            f"selected min={stats['min_k']} max={stats['max_k']} "
            f"mean={stats['mean_k']} <10={stats['lt_10']} =10={stats['eq_10']}"
        )


if __name__ == "__main__":
    main()
