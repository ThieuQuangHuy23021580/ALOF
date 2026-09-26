from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from backend.application.services.adaptive_models import (
    DiagnosisResult,
    QuizSpecification,
    RetrievedMemory,
)
from backend.application.services.adaptive_retrieval_service import (
    AdaptiveRetrievalService,
)
from backend.application.services.diagnosis_engine import (
    DiagnosisEngine,
)
from backend.application.services.evidence_aggregator import (
    EvidenceAggregator,
)
from backend.application.services.quiz_specification import (
    QuizSpecificationBuilder,
)


@dataclass(frozen=True)
class AdaptiveDiagnosisResult:
    """
    Complete internal adaptive result.

    This object must be adapted before entering
    benchmark output.
    """

    memories: list[RetrievedMemory]
    diagnosis: DiagnosisResult
    quiz: QuizSpecification


class AdaptiveDiagnosisService:
    """
    End-to-end adaptive retrieval + diagnosis pipeline.

    Important:
        This service does NOT modify the existing benchmark
        output format.
    """

    def __init__(
        self,
        retrieval: AdaptiveRetrievalService,
        aggregator: EvidenceAggregator,
        diagnosis_engine: DiagnosisEngine,
        quiz_builder: QuizSpecificationBuilder,
    ) -> None:

        self._retrieval = retrieval
        self._aggregator = aggregator
        self._diagnosis = diagnosis_engine
        self._quiz_builder = quiz_builder

    def run(
        self,
        learner_id: str,
        current_text: str,
        target_concept_ids: list[str],
        top_k: int | None = None,
        now: datetime | None = None,
    ) -> AdaptiveDiagnosisResult:

        memories = self._retrieval.retrieve(
            learner_id=learner_id,
            current_text=current_text,
            target_concept_ids=target_concept_ids,
            top_k=top_k,
            now=now,
        )

        evidence = (
            self._aggregator.aggregate(
                memories=memories,
                target_concept_ids=target_concept_ids,
            )
        )

        diagnosis = (
            self._diagnosis.diagnose(
                evidence=evidence,
                target_concept_ids=target_concept_ids,
            )
        )

        quiz = (
            self._quiz_builder.build(
                diagnosis
            )
        )

        return AdaptiveDiagnosisResult(
            memories=memories,
            diagnosis=diagnosis,
            quiz=quiz,
        )