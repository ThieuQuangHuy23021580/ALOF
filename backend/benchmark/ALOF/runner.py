from __future__ import annotations
from datetime import datetime
import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from backend.application.orchestration.execution_request import (
    ExecutionRequest,
)
from backend.application.orchestration.orchestrator_factory import (
    create_learning_orchestrator,
)
from backend.domain.learning.learning_interaction import (
    LearningInteraction,
)
from backend.domain.learning.learning_state import (
    LearningState,
)
from backend.domain.student.student import Student

from .adapter import ALOFDatasetAdapter


class ALOFBenchmarkRunner:
    """
    Run the real ALOF orchestration pipeline
    on the ALOF-native benchmark dataset.
    """

    def __init__(
        self,
        dataset_path: str | Path,
    ) -> None:
        self.adapter = ALOFDatasetAdapter(dataset_path)
        self.orchestrator = create_learning_orchestrator()

    # ======================================================
    # Dataset -> LearningState
    # ======================================================

    def build_learning_state(
        self,
        sample: dict[str, Any],
    ) -> LearningState:
        learner = sample["learner"]

        learner_id = str(
            learner.get("id")
            or learner.get("learner_id")
            or sample["case_id"]
        )

        state = LearningState(
            learner_id=learner_id,
        )

        for raw in sample["history"]:
            if not isinstance(raw, dict):
                continue

            interaction_data: dict[str, Any] = {
                "learner_id": learner_id,
                "question_id": raw.get(
                    "question_id"
                ),
                "question": str(
                    raw.get("question", "")
                ),
                "answer": str(
                    raw.get("answer", "")
                ),
                "correct": raw.get("correct"),
                "concept_ids": list(
                    raw.get("concept_ids", [])
                ),
            }

            # Preserve dataset timestamp so that
            # temporal / long-gap cases are meaningful.
            timestamp = raw.get("timestamp")

            if timestamp is not None:
                interaction_data["timestamp"] = (
                    self._parse_timestamp(timestamp)
                )

            metadata = raw.get("metadata")

            if isinstance(metadata, dict):
                interaction_data["metadata"] = metadata

            interaction = LearningInteraction(
                **interaction_data,
            )

            state.add_interaction(interaction)

        return state

    @staticmethod
    def _parse_timestamp(
        value: Any,
    ) -> datetime:
        """
        Normalize dataset timestamps to UTC.

        Supports:
        - datetime
        - ISO-8601 strings
        - Unix timestamps
        """

        if isinstance(value, datetime):
            timestamp = value

        elif isinstance(value, (int, float)):
            timestamp = datetime.fromtimestamp(
                value,
                tz=UTC,
            )

        else:
            text = str(value).strip()

            if not text:
                return datetime.fromtimestamp(
                    0,
                    tz=UTC,
                )

            try:
                timestamp = datetime.fromisoformat(
                    text.replace(
                        "Z",
                        "+00:00",
                    )
                )
            except ValueError:
                return datetime.fromtimestamp(
                    0,
                    tz=UTC,
                )

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(
                tzinfo=UTC,
            )

        return timestamp.astimezone(UTC)

    # ======================================================
    # Dataset -> ExecutionRequest
    # ======================================================

    def build_request(
        self,
        sample: dict[str, Any],
    ) -> ExecutionRequest:
        learner = sample["learner"]

        learner_id = str(
            learner.get("id")
            or learner.get("learner_id")
            or sample["case_id"]
        )

        student = Student(
            id=learner_id,
            display_name=str(
                learner.get(
                    "name",
                    learner_id,
                )
            ),
        )

        return ExecutionRequest(
            student=student,
            message=self.adapter.build_message(
                sample
            ),
            learning_state=self.build_learning_state(
                sample
            ),
            metadata=self.adapter.build_request_metadata(
                sample
            ),
        )

    # ======================================================
    # Single case
    # ======================================================

    def run_case(
        self,
        sample: dict[str, Any],
    ) -> dict[str, Any]:
        request = self.build_request(sample)

        result = self.orchestrator.execute(
            request
        )

        artifact = result.final_artifact

        prediction = None

        if artifact is not None:
            prediction = getattr(
                artifact,
                "content",
                None,
            )

        return {
            "case_id": sample["case_id"],
            "prediction": prediction,
            "runtime_metadata": result.metadata,
        }

    # ======================================================
    # Quota detection
    # ======================================================

    @staticmethod
    def is_quota_error(
        exc: BaseException,
    ) -> bool:
        """
        Detect provider quota / token exhaustion errors.

        This is intentionally kept in the benchmark runner
        and does not introduce provider-specific logic into
        the ALOF core.
        """

        text = str(exc).lower()

        quota_markers = (
            "token per day",
            "tokens per day",
            "token_per_day",
            "tokens_per_day",
            "daily token",
            "daily tokens",
            "quota exceeded",
            "quota_exceeded",
            "rate limit",
            "rate_limit",
            "ratelimit",
            "resource exhausted",
            "resource_exhausted",
            "too many requests",
            "tpm",
            "rpm",
        )

        return any(
            marker in text
            for marker in quota_markers
        )

    # ======================================================
    # Output
    # ======================================================

    @staticmethod
    def load_existing_results(
        output_path: str | Path,
    ) -> dict[str, dict[str, Any]]:
        """
        Load existing results indexed by case_id.

        Only successful cases are considered completed.
        Failed cases can be retried on the next run.
        """

        output = Path(output_path)

        if not output.exists():
            return {}

        existing: dict[str, dict[str, Any]] = {}

        with output.open(
            "r",
            encoding="utf-8",
        ) as f:
            for line_no, line in enumerate(
                f,
                start=1,
            ):
                line = line.strip()

                if not line:
                    continue

                try:
                    result = json.loads(line)

                except json.JSONDecodeError:
                    print(
                        f"Warning: ignoring invalid JSON "
                        f"at {output}:{line_no}"
                    )
                    continue

                if not isinstance(result, dict):
                    continue

                case_id = result.get("case_id")

                if case_id is None:
                    continue

                existing[str(case_id)] = result

        return existing

    @staticmethod
    def write_results(
        output_path: str | Path,
        results: dict[str, dict[str, Any]],
    ) -> None:
        """
        Persist results sorted by case_id.

        Existing results are preserved, while updated/retried
        cases are written back into their logical case_id order.
        """

        output = Path(output_path)

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        sorted_results = sorted(
            results.values(),
            key=lambda result: result.get(
                "case_id",
                "",
            ),
        )

        with output.open(
            "w",
            encoding="utf-8",
        ) as f:
            for result in sorted_results:
                f.write(
                    json.dumps(
                        result,
                        ensure_ascii=False,
                        default=lambda obj: (
                            obj.isoformat()
                            if isinstance(obj, datetime)
                            else str(obj)
                        ),
                    )
                    + "\n"
                )

    # ======================================================
    # Benchmark
    # ======================================================

    def run(
        self,
        output_path: str | Path | None = None,
        start: int = 0,
        limit: int | None = None,
        stop_on_quota: bool = False,
    ) -> list[dict[str, Any]]:

        if start < 0:
            raise ValueError(
                "start must be >= 0."
            )

        if limit is not None and limit < 1:
            raise ValueError(
                "limit must be >= 1."
            )

        samples = list(
            self.adapter.iter_samples()
        )

        total_cases = len(samples)

        if start >= total_cases:
            raise ValueError(
                f"start={start} is outside the dataset "
                f"with {total_cases} cases."
            )

        end = total_cases

        if limit is not None:
            end = min(
                start + limit,
                total_cases,
            )

        selected_samples = samples[
            start:end
        ]

        # --------------------------------------------------
        # Load existing results
        # --------------------------------------------------

        existing_results: dict[
            str,
            dict[str, Any],
        ] = {}

        if output_path is not None:
            existing_results = (
                self.load_existing_results(
                    output_path
                )
            )

            # Always normalize the existing file order,
            # even when no new case is executed.
            if existing_results:
                self.write_results(
                    output_path,
                    existing_results,
                )

        completed_case_ids = {
            case_id
            for case_id, result
            in existing_results.items()
            if result.get("success") is True
        }

        print(
            f"Dataset cases: {total_cases}"
        )

        print(
            f"Requested index range: "
            f"{start} -> {end - 1}"
        )

        print(
            f"Requested cases: "
            f"{len(selected_samples)}"
        )

        print(
            f"Existing results: "
            f"{len(existing_results)}"
        )

        print(
            f"Completed cases: "
            f"{len(completed_case_ids)}"
        )

        print(
            f"Stop on quota: "
            f"{stop_on_quota}"
        )

        print()

        executed_results: list[
            dict[str, Any]
        ] = []

        skipped = 0
        stopped_reason: str | None = None

        for local_index, sample in enumerate(
            selected_samples
        ):
            index = start + local_index

            case_id = str(
                sample["case_id"]
            )

            # --------------------------------------------------
            # Skip already successful case
            # --------------------------------------------------

            if case_id in completed_case_ids:
                skipped += 1

                print(
                    f"[{local_index + 1}/"
                    f"{len(selected_samples)}] "
                    f"Skipping index={index}, "
                    f"case={case_id} "
                    f"(already completed)"
                )

                continue

            # --------------------------------------------------
            # Run case
            # --------------------------------------------------

            print(
                f"[{local_index + 1}/"
                f"{len(selected_samples)}] "
                f"Running index={index}, "
                f"case={case_id}"
            )

            started_at = datetime.now(
                UTC
            )

            try:
                result = self.run_case(
                    sample
                )

                result["success"] = True

            except Exception as exc:
                quota_error = self.is_quota_error(
                    exc
                )

                result = {
                    "case_id": case_id,
                    "success": False,
                    "error": (
                        f"{type(exc).__name__}: "
                        f"{exc}"
                    ),
                    "quota_error": quota_error,
                }

            result["index"] = index

            result["started_at"] = (
                started_at.isoformat()
            )

            result["finished_at"] = (
                datetime.now(
                    UTC
                ).isoformat()
            )

            # --------------------------------------------------
            # Upsert by case_id
            # --------------------------------------------------

            existing_results[case_id] = result

            executed_results.append(
                result
            )

            # --------------------------------------------------
            # Persist immediately
            # --------------------------------------------------

            if output_path is not None:
                self.write_results(
                    output_path,
                    existing_results,
                )

            # --------------------------------------------------
            # Quota handling
            # --------------------------------------------------

            if (
                result.get(
                    "quota_error",
                    False,
                )
                and stop_on_quota
            ):
                stopped_reason = (
                    "quota_exhausted"
                )

                print()
                print(
                    "Quota/token limit detected."
                )
                print(
                    "Stopping benchmark."
                )

                break

            print(
                "  -> success"
                if result["success"]
                else "  -> failed"
            )

        # ==================================================
        # Summary
        # ==================================================

        success = sum(
            1
            for item in executed_results
            if item["success"]
        )

        failed = sum(
            1
            for item in executed_results
            if not item["success"]
        )

        print()
        print(
            "=" * 60
        )

        print(
            "ALOF benchmark finished."
        )

        print(
            f"Executed: {len(executed_results)}"
        )

        print(
            f"Skipped:  {skipped}"
        )

        print(
            f"Success:  {success}"
        )

        print(
            f"Failed:   {failed}"
        )

        if stopped_reason is not None:
            print(
                f"Stopped:  {stopped_reason}"
            )

        if output_path is not None:
            print(
                f"Results:  {output_path}"
            )

        print(
            "=" * 60
        )

        return executed_results


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run the ALOF-native adaptive-learning "
            "benchmark."
        )
    )

    parser.add_argument(
        "--dataset",
        default=(
            "backend/benchmark/ALOF/"
            "data/adaptive_learning_vi_longcontext.jsonl"
        ),
        help="Path to the benchmark dataset.",
    )

    parser.add_argument(
        "--output",
        default=(
            "backend/benchmark/ALOF/"
            "results/results_longcontext.jsonl"
        ),
        help="Path to the JSONL result file.",
    )

    parser.add_argument(
        "--start",
        type=int,
        default=0,
        help=(
            "Dataset index to start from "
            "(default: 0)."
        ),
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help=(
            "Maximum number of cases to run "
            "(default: all remaining cases)."
        ),
    )

    parser.add_argument(
        "--stop-on-quota",
        action="store_true",
        help=(
            "Stop immediately when a quota/token "
            "limit error is detected."
        ),
    )

    args = parser.parse_args()

    runner = ALOFBenchmarkRunner(
        args.dataset
    )

    runner.run(
        output_path=args.output,
        start=args.start,
        limit=args.limit,
        stop_on_quota=args.stop_on_quota,
    )


if __name__ == "__main__":
    main()