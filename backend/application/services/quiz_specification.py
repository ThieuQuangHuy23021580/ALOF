from __future__ import annotations

from backend.application.services.adaptive_models import (
    DiagnosisResult,
    QuizSpecification,
)


class QuizSpecificationBuilder:
    """
    Converts diagnosis into quiz targeting information.

    This is intentionally NOT a general strategy engine.
    """

    def build(
        self,
        diagnosis: DiagnosisResult,
    ) -> QuizSpecification:

        if diagnosis.weak_concepts:
            targets = list(
                diagnosis.weak_concepts
            )
            reason = "weak_concept"

        elif diagnosis.primary_concept:
            targets = [
                diagnosis.primary_concept
            ]
            reason = "primary_diagnosis"

        else:
            targets = []
            reason = "insufficient_evidence"

        difficulty = (
            self._difficulty(
                diagnosis.level
            )
        )

        return QuizSpecification(
            target_concepts=targets,
            difficulty=difficulty,
            reason=reason,
            evidence_interaction_ids=(
                diagnosis.evidence_interaction_ids
            ),
        )

    @staticmethod
    def _difficulty(
        level: str,
    ) -> str:

        normalized = (
            str(level or "")
            .strip()
            .lower()
        )

        if normalized == "beginner":
            return "beginner"

        if normalized == "advanced":
            return "advanced"

        return "medium"