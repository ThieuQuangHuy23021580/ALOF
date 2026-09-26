from __future__ import annotations

from backend.application.services.adaptive_models import (
    DiagnosisResult,
    RetrievedMemory,
)


class BenchmarkCompatibilityAdapter:
    """
    Convert rich internal adaptive results into the
    existing ALOF benchmark output schema.

    Do not expose internal retrieval/diagnostic metadata.
    """

    @staticmethod
    def memory_output(
        memories: list[RetrievedMemory],
    ) -> dict:
        """
        Existing benchmark memory representation.
        """

        return {
            "question_ids": [
                memory.question_id
                for memory in memories
            ]
        }

    @staticmethod
    def diagnosis_output(
        result: DiagnosisResult,
    ) -> dict:
        """
        Existing benchmark diagnosis representation.

        Only the established fields are emitted.
        """

        return {
            "concept": result.primary_concept,
            "level": result.level,
            "weak_concepts": list(
                result.weak_concepts
            ),
        }