from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from backend.application.runtime.evidence_selector import EvidenceSelector
from backend.domain.learning.historical_evidence_builder import (
    HistoricalEvidenceBuilder,
)
from backend.domain.learning.learning_interaction import LearningInteraction
from backend.domain.learning.learning_state import LearningState
from backend.infrastructure.prompts.context_builder import ContextBuilder


def parse_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        timestamp = value
    elif isinstance(value, (int, float)):
        timestamp = datetime.fromtimestamp(value, tz=UTC)
    else:
        text = str(value or "").strip()
        if not text:
            return datetime.fromtimestamp(0, tz=UTC)
        try:
            timestamp = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return datetime.fromtimestamp(0, tz=UTC)

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=UTC)
    return timestamp.astimezone(UTC)


def build_learning_state(sample: dict[str, Any]) -> LearningState:
    learner_id = str(
        sample["learner"].get("learner_id")
        or sample["learner"].get("id")
        or sample["case_id"]
    )
    state = LearningState(learner_id=learner_id)

    for raw in sample["history"]:
        state.add_interaction(
            LearningInteraction(
                learner_id=learner_id,
                question_id=str(raw.get("question_id") or ""),
                question=str(raw.get("question") or ""),
                answer=str(raw.get("answer") or ""),
                correct=raw.get("correct"),
                concept_ids=list(raw.get("concept_ids") or []),
                timestamp=parse_timestamp(raw.get("timestamp")),
            )
        )
    return state


def compute_memory_gold(sample: dict[str, Any]) -> dict[str, list[str]]:
    task = sample["current_task"]
    question = str(task.get("question") or task.get("content") or "")
    concept_ids = [str(v) for v in (task.get("concept_ids") or [])]

    state = build_learning_state(sample)
    evidence = HistoricalEvidenceBuilder(recent_limit=5).build(
        learning_state=state,
        current_question=question,
        related_concept_ids=concept_ids,
    )

    # relevant = concept overlap (audit field)
    relevant_ids = sorted(
        {
            str(i.question_id).strip()
            for i in evidence.relevant_interactions
            if i.question_id
        }
    )

    # pool giống ContextBuilder: dedupe(relevant + recent) theo interaction.id
    seen_ids: set[str] = set()
    interactions: list[dict[str, Any]] = []

    for interaction in (
        list(evidence.relevant_interactions)
        + list(evidence.recent_interactions)
    ):
        if interaction.id in seen_ids:
            continue
        seen_ids.add(interaction.id)
        interactions.append(interaction.model_dump(mode="json"))

    selection = EvidenceSelector.select(
        current_question=question,
        current_concept_ids=concept_ids,
        interactions=interactions,
        related_history=[],
        top_k=ContextBuilder.MEMORY_TOP_K,
        max_tokens=ContextBuilder.MEMORY_MAX_TOKENS,
    )

    top_k_ids: list[str] = []
    for record in selection["history"] + selection["related_history"]:
        qid = str(record.get("question_id") or record.get("id") or "").strip()
        if qid:
            top_k_ids.append(qid)

    return {
        "relevant_interactions": relevant_ids,
        "top_k_interactions": top_k_ids,
    }


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

            memory["relevant_interactions"] = memory_gold["relevant_interactions"]
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