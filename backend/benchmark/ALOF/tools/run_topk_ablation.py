"""
Run the ALOF benchmark at multiple topK values and write results /
reports / failure_reports into per-topK subfolders.

Datasets are processed in priority order:
    1. long_context   (2 files)
    2. multi_concept  (3 files)
    3. strategy       (3 files)

Total: 8 datasets × 50 cases = 400 cases per topK.

For each topK in {3, 5, 8}:
    - Set ADAPTIVE_RETRIEVAL_TOP_K
    - Run the LLM benchmark (backend.benchmark.ALOF.runner)
        results ->  backend/benchmark/ALOF/results/topK_<N>/results_<split>_<diff>.jsonl
    - Run the evaluator
        report   ->  backend/benchmark/ALOF/reports/topK_<N>/report_<split>_<diff>.json
        failure  ->  backend/benchmark/ALOF/failure_reports/topK_<N>/failure_report_<split>_<diff>.json

The script prints per-dataset progress and continues to the next
dataset even if one fails (e.g. all 5 API keys exhausted).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


# -----------------------------------------------------------
# Project paths
# -----------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
ALOF_DIR = SCRIPT_DIR.parent
REPO_ROOT = ALOF_DIR.parents[2]

RESULTS_DIR = ALOF_DIR / "results"
REPORTS_DIR = ALOF_DIR / "reports"
FAILURE_DIR = ALOF_DIR / "failure_reports"


# -----------------------------------------------------------
# Datasets (priority order: long_context > multi_concept > strategy)
# -----------------------------------------------------------

DATASETS: list[tuple[str, str, str, str]] = [
    # (split_label, difficulty, dataset_relpath, results_basename)
    (
        "longcontext", "easy",
        "data/long_context/adaptive_learning_vi_longcontext_easy.jsonl",
        "results_longcontext_easy.jsonl",
    ),
    (
        "longcontext", "medium",
        "data/long_context/adaptive_learning_vi_longcontext_medium.jsonl",
        "results_longcontext_medium.jsonl",
    ),
    (
        "multiconcept", "easy",
        "data/multi_concept/adaptive_learning_vi_multiconcept_easy.jsonl",
        "results_multiconcept_easy.jsonl",
    ),
    (
        "multiconcept", "medium",
        "data/multi_concept/adaptive_learning_vi_multiconcept_medium.jsonl",
        "results_multiconcept_medium.jsonl",
    ),
    (
        "multiconcept", "hard",
        "data/multi_concept/adaptive_learning_vi_multiconcept_hard.jsonl",
        "results_multiconcept_hard.jsonl",
    ),
    (
        "strategy", "easy",
        "data/strategy/adaptive_learning_vi_strategy_easy.jsonl",
        "results_strategy_easy.jsonl",
    ),
    (
        "strategy", "medium",
        "data/strategy/adaptive_learning_vi_strategy_medium.jsonl",
        "results_strategy_medium.jsonl",
    ),
    (
        "strategy", "hard",
        "data/strategy/adaptive_learning_vi_strategy_hard.jsonl",
        "results_strategy_hard.jsonl",
    ),
]


# -----------------------------------------------------------
# Per-topK paths
# -----------------------------------------------------------

def topk_paths(topk: int) -> dict[str, Path]:
    name = f"topK_{topk}"
    return {
        "results": RESULTS_DIR / name,
        "reports": REPORTS_DIR / name,
        "failure": FAILURE_DIR / name,
    }


def ensure_dirs(paths: dict[str, Path]) -> None:
    for p in paths.values():
        p.mkdir(parents=True, exist_ok=True)


# -----------------------------------------------------------
# Subprocess helpers
# -----------------------------------------------------------

def run_subprocess(
    cmd: list[str],
    *,
    env: dict[str, str] | None = None,
    timeout: int | None = None,
) -> tuple[int, str, str]:
    """
    Run cmd synchronously, return (returncode, stdout, stderr).

    Stdout/stderr are also streamed to the current terminal line-by-line
    so the user can watch progress as the subprocess runs. The full
    captured output is returned for the caller's post-mortem.
    """
    print(f"\n[exec] {' '.join(cmd)}", flush=True)
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=str(REPO_ROOT),
        env=env,
    )

    captured: list[str] = []
    assert proc.stdout is not None

    try:
        for line in iter(proc.stdout.readline, ""):
            captured.append(line)
            print(line, end="", flush=True)
        proc.stdout.close()
        returncode = proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        captured.append("\n[timeout] subprocess killed\n")
        return (
            -1,
            "".join(captured),
            "[timeout] subprocess killed",
        )

    return (
        returncode,
        "".join(captured),
        "",
    )


# -----------------------------------------------------------
# Per-dataset execution
# -----------------------------------------------------------

def count_cases(dataset_abs: Path) -> int:
    with dataset_abs.open(encoding="utf-8") as f:
        return sum(
            1
            for line in f
            if line.strip()
        )


def run_runner_for_dataset(
    *,
    topk: int,
    dataset_rel: str,
    output_abs: Path,
    stop_on_quota: bool,
) -> bool:
    """
    Run the LLM benchmark for one dataset. Returns True if
    every case completed (success or deterministic fail).
    """
    cmd = [
        sys.executable,
        "-m",
        "backend.benchmark.ALOF.runner",
        "--dataset",
        dataset_rel,
        "--output",
        str(output_abs),
        "--stop-on-quota" if stop_on_quota else "",
    ]
    cmd = [c for c in cmd if c]

    env = dict(os.environ)
    env["ADAPTIVE_RETRIEVAL_TOP_K"] = str(topk)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    env["PYTHONPATH"] = (
        str(REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    )

    rc, _, stderr = run_subprocess(cmd, env=env)
    return rc == 0


def run_evaluator_for_dataset(
    *,
    dataset_rel: str,
    results_abs: Path,
    report_abs: Path,
    failure_abs: Path,
) -> bool:
    """Run the semantic evaluator for one dataset."""
    cmd = [
        sys.executable,
        "-X",
        "utf8",
        "-m",
        "backend.benchmark.ALOF.evaluator",
        "--dataset",
        dataset_rel,
        "--results",
        str(results_abs),
        "--report",
        str(report_abs),
        "--failure-report",
        str(failure_abs),
    ]

    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    env["PYTHONPATH"] = (
        str(REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    )

    rc, _, _ = run_subprocess(cmd, env=env)
    return rc == 0


# -----------------------------------------------------------
# Top-level orchestration
# -----------------------------------------------------------

def run_for_topk(
    topk: int,
    *,
    resume: bool,
    stop_on_quota: bool,
) -> dict[str, Any]:
    paths = topk_paths(topk)
    ensure_dirs(paths)

    print(f"\n{'#' * 70}")
    print(f"# topK = {topk}")
    print(f"# results -> {paths['results']}")
    print(f"# reports -> {paths['reports']}")
    print(f"# failure -> {paths['failure']}")
    print(f"{'#' * 70}\n")

    summary: list[dict[str, Any]] = []

    for (
        split,
        difficulty,
        dataset_rel,
        results_basename,
    ) in DATASETS:
        dataset_abs = REPO_ROOT / "backend" / "benchmark" / "ALOF" / dataset_rel
        results_abs = paths["results"] / results_basename
        report_abs = paths["reports"] / (
            f"report_{split}_{difficulty}.json"
        )
        failure_abs = paths["failure"] / (
            f"failure_report_{split}_{difficulty}.json"
        )

        n_cases = (
            count_cases(dataset_abs)
            if dataset_abs.exists()
            else 0
        )

        print(
            f"\n=== topK={topk} | {split} / {difficulty} "
            f"| {n_cases} cases ==="
        )

        # Skip if results already exist and --resume
        if (
            resume
            and results_abs.exists()
            and sum(1 for _ in results_abs.open(encoding="utf-8"))
            >= n_cases
        ):
            print(
                f"[skip] {results_abs.name} already complete "
                f"({n_cases} cases)"
            )
        else:
            ok = run_runner_for_dataset(
                topk=topk,
                dataset_rel=(
                    f"backend/benchmark/ALOF/{dataset_rel}"
                ),
                output_abs=results_abs,
                stop_on_quota=stop_on_quota,
            )
            if not ok:
                print(
                    f"[warn] runner failed for "
                    f"{split}/{difficulty}, continuing"
                )
                # continue to next; do not abort the whole run

        # Always run evaluator (idempotent, will report whatever exists)
        if results_abs.exists():
            ok_eval = run_evaluator_for_dataset(
                dataset_rel=(
                    f"backend/benchmark/ALOF/{dataset_rel}"
                ),
                results_abs=results_abs,
                report_abs=report_abs,
                failure_abs=failure_abs,
            )
            if not ok_eval:
                print(
                    f"[warn] evaluator failed for "
                    f"{split}/{difficulty}"
                )
        else:
            ok_eval = False
            print(
                f"[skip] no results file at {results_abs}, "
                f"evaluator not run"
            )

        summary.append(
            {
                "split": split,
                "difficulty": difficulty,
                "n_cases": n_cases,
                "results_path": str(results_abs),
                "report_path": str(report_abs),
                "failure_path": str(failure_abs),
                "runner_ok": ok_eval or results_abs.exists(),
            }
        )

    return {
        "topK": topk,
        "datasets": summary,
        "total_cases": sum(s["n_cases"] for s in summary),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run ALOF benchmark across multiple topK values "
            "with per-topK output folders."
        )
    )
    parser.add_argument(
        "--topk",
        type=int,
        nargs="+",
        default=[3, 5, 8],
        help="topK values to run (default: 3 5 8)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help=(
            "Skip datasets whose results file is already complete "
            "(case count matches dataset length)."
        ),
    )
    parser.add_argument(
        "--no-stop-on-quota",
        action="store_true",
        help=(
            "Do not abort on quota errors; let the fallback "
            "manager try the next key automatically. "
            "(Default: stop on quota, so we resume later.)"
        ),
    )
    parser.add_argument(
        "--datasets",
        choices=["all", "long_multiconcept_strategy", "long_multiconcept"],
        default="all",
        help=(
            "Which dataset family to execute. Default 'all' covers "
            "all 8 datasets (long_context + multi_concept + strategy)."
        ),
    )
    args = parser.parse_args()

    overall_start = time.time()
    overall_summary: list[dict[str, Any]] = []

    for topk in args.topk:
        start = time.time()
        try:
            result = run_for_topk(
                topk,
                resume=args.resume,
                stop_on_quota=not args.no_stop_on_quota,
            )
        except KeyboardInterrupt:
            print(
                f"\n[interrupt] aborted at topK={topk}, "
                f"progress is persisted on disk."
            )
            break
        result["duration_seconds"] = round(
            time.time() - start,
            1,
        )
        overall_summary.append(result)
        print(
            f"\n[done] topK={topk} "
            f"({result['total_cases']} cases) "
            f"in {result['duration_seconds']}s"
        )

    total_elapsed = round(time.time() - overall_start, 1)
    out_summary = {
        "topks_run": args.topk,
        "total_cases_per_topK": (
            8 * 50
        ),
        "total_elapsed_seconds": total_elapsed,
        "results": overall_summary,
    }
    summary_path = (
        REPO_ROOT
        / "backend"
        / "benchmark"
        / "ALOF"
        / "topK_ablation_summary.json"
    )
    summary_path.write_text(
        json.dumps(
            out_summary,
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )

    print(f"\n[summary] {summary_path}")
    print(f"[summary] total elapsed: {total_elapsed}s")


if __name__ == "__main__":
    main()