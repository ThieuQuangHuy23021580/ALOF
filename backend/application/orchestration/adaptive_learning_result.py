from __future__ import annotations

from pydantic import BaseModel

from backend.domain.learning.adaptive_teaching_action import (
    AdaptiveTeachingAction,
)
from backend.domain.learning.historical_evidence import (
    HistoricalEvidence,
)
from backend.domain.learning.knowledge_diagnosis import (
    KnowledgeDiagnosis,
)


class AdaptiveLearningResult(BaseModel):
    """
    Complete adaptive-learning result for one
    tutoring execution.

    Contains the three stages required by the
    adaptive learning pipeline:

        HistoricalEvidence
            ↓
        KnowledgeDiagnosis
            ↓
        AdaptiveTeachingAction
    """

    evidence: HistoricalEvidence

    diagnosis: KnowledgeDiagnosis

    teaching_action: AdaptiveTeachingAction