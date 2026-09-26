from __future__ import annotations

from backend.application.services.adaptive_diagnosis_service import (
    AdaptiveDiagnosisService,
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
from backend.config.adaptive_retrieval import (
    AdaptiveRetrievalConfig,
)
from backend.domain.learning.memory_repository import (
    MemoryRepository,
)


def build_adaptive_diagnosis_service(
    memory_repository: MemoryRepository,
    config: AdaptiveRetrievalConfig | None = None,
) -> AdaptiveDiagnosisService:

    config = (
        config
        or AdaptiveRetrievalConfig()
    )

    retrieval = (
        AdaptiveRetrievalService(
            repository=memory_repository,
            config=config,
        )
    )

    aggregator = EvidenceAggregator()

    diagnosis = DiagnosisEngine(
        config=config,
    )

    quiz_builder = (
        QuizSpecificationBuilder()
    )

    return AdaptiveDiagnosisService(
        retrieval=retrieval,
        aggregator=aggregator,
        diagnosis_engine=diagnosis,
        quiz_builder=quiz_builder,
    )