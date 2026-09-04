
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator


class ALOFDatasetAdapter:
    """Load and normalize the ALOF-native adaptive-learning benchmark."""

    def __init__(self, dataset_path: str | Path) -> None:
        self.dataset_path = Path(dataset_path)

    def load(self) -> list[dict[str, Any]]:
        samples: list[dict[str, Any]] = []

        with self.dataset_path.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()

                if not line:
                    continue

                sample = json.loads(line)

                if not isinstance(sample, dict):
                    raise ValueError(
                        f"Line {line_no}: sample must be an object."
                    )

                self.validate(sample, line_no)
                samples.append(sample)

        return samples

    def iter_samples(self) -> Iterator[dict[str, Any]]:
        yield from self.load()

    @staticmethod
    def validate(
        sample: dict[str, Any],
        line_no: int = 0,
    ) -> None:
        required = {
            "case_id",
            "learner",
            "history",
            "current_task",
            "expected",
        }

        missing = required - sample.keys()

        if missing:
            prefix = f"Line {line_no}: " if line_no else ""
            raise ValueError(
                f"{prefix}missing fields: {sorted(missing)}"
            )

        if not isinstance(sample["history"], list):
            raise ValueError("history must be a list.")

        if not isinstance(sample["expected"], dict):
            raise ValueError("expected must be an object.")

    @staticmethod
    def build_message(
        sample: dict[str, Any],
    ) -> str:
        task = sample["current_task"]

        if isinstance(task, dict):
            return str(
                task.get("question")
                or task.get("prompt")
                or task.get("content")
                or ""
            )

        return str(task)

    @staticmethod
    def build_request_metadata(
        sample: dict[str, Any],
    ) -> dict[str, Any]:
        task = sample["current_task"]

        if not isinstance(task, dict):
            task = {"content": str(task)}

        return {
            "benchmark": "alof",
            "benchmark_case_id": sample["case_id"],
            "current_question": task.get(
                "question",
                task.get("content", ""),
            ),
            "current_concept_ids": task.get(
                "concept_ids",
                [],
            ),
            "alof_benchmark": True,
        }

