from __future__ import annotations

from dataclasses import dataclass

from backend.domain.learning.adaptive_teaching_action import (
    AdaptiveTeachingAction,
    AdaptiveTeachingActionSelector,
)
from backend.domain.learning.historical_evidence import (
    HistoricalEvidence,
)
from backend.domain.learning.historical_evidence_builder import (
    HistoricalEvidenceBuilder,
)
from backend.domain.learning.knowledge_diagnosis import (
    KnowledgeDiagnosis,
    KnowledgeStateDiagnoser,
)
from backend.domain.learning.learning_state import (
    LearningState,
)
from backend.application.orchestration.adaptive_learning_result import (
    AdaptiveLearningResult,
)

class AdaptiveLearningPipeline:
    """
    Application-level coordinator for adaptive learning.

    Responsibilities
    ----------------
    - Build historical evidence from LearningState.
    - Diagnose the learner's knowledge state.
    - Select an adaptive teaching action.
    - Keep the three stages explicitly separated.
    - Never execute teaching.
    - Never modify LearningState directly.
    - Never call an LLM.

    The resulting AdaptiveLearningResult can then be
    consumed by the planner and runtime.
    """

    def __init__(
        self,
        evidence_builder: HistoricalEvidenceBuilder | None = None,
        diagnoser: KnowledgeStateDiagnoser | None = None,
        action_selector: AdaptiveTeachingActionSelector | None = None,
    ) -> None:

        self._evidence_builder = (
            evidence_builder
            if evidence_builder is not None
            else HistoricalEvidenceBuilder()
        )

        self._diagnoser = (
            diagnoser
            if diagnoser is not None
            else KnowledgeStateDiagnoser()
        )

        self._action_selector = (
            action_selector
            if action_selector is not None
            else AdaptiveTeachingActionSelector()
        )

    def run(
        self,
        learning_state: LearningState,
        current_question: str = "",
        related_concept_ids: list[str] | None = None,
        primary_concept_ids: list[str] | None = None,
    ) -> AdaptiveLearningResult:
        """
        Execute the complete adaptive learning pipeline.

        Parameters
        ----------
        learning_state:
            Current learner model.

        current_question:
            Question currently being solved or taught.

        related_concept_ids:
            Concepts identified as related to the current task.
            These are passed to historical evidence acquisition.

        primary_concept_ids:
            Concepts that are primary targets of the current task.
            These are passed to knowledge diagnosis.

        Returns
        -------
        AdaptiveLearningResult
            Contains evidence, diagnosis and teaching action.
        """

        # ======================================================
        # 1. HISTORICAL EVIDENCE
        # ======================================================

        evidence = self._evidence_builder.build(
            learning_state=learning_state,
            current_question=current_question,
            related_concept_ids=related_concept_ids,
        )

        # ======================================================
        # 2. KNOWLEDGE DIAGNOSIS
        # ======================================================

        diagnosis = self._diagnoser.diagnose(
            learning_state=learning_state,
            evidence=evidence,
            primary_concept_ids=primary_concept_ids,
        )

        # ======================================================
        # 3. ADAPTIVE TEACHING ACTION
        # ======================================================

        teaching_action = self._action_selector.select(
            diagnosis,
        )

        # ======================================================
        # RESULT
        # ======================================================

        return AdaptiveLearningResult(
            evidence=evidence,
            diagnosis=diagnosis,
            teaching_action=teaching_action,
        )