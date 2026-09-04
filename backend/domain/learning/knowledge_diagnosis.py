from __future__ import annotations

from pydantic import BaseModel, Field

from backend.domain.knowledge.knowledge_level import (
    KnowledgeLevel,
)
from backend.domain.learning.historical_evidence import (
    HistoricalEvidence,
)
from backend.domain.learning.learning_state import (
    LearningState,
)


class ConceptDiagnosis(BaseModel):
    """
    Diagnosis of one learner knowledge concept.

    This is a domain-level diagnostic result.
    It does not call an LLM and does not modify
    the learner state.
    """

    concept_id: str

    mastery: float = 0.0

    level: KnowledgeLevel = KnowledgeLevel.BEGINNER

    attempts: int = 0

    correct_attempts: int = 0

    accuracy: float = 0.0

    error_rate: float = 0.0

    evidence_count: int = 0

    has_recent_evidence: bool = False

    has_relevant_evidence: bool = False

    weakness_signal: bool = False

    transfer_deficit_signal: bool = False


class KnowledgeDiagnosis(BaseModel):
    """
    Represents the diagnosed learner knowledge state
    for the current tutoring task.

    KnowledgeDiagnosis is produced from historical evidence
    and the current learner state.

    It does not modify LearningState.
    """

    learner_id: str

    current_question: str = ""

    concepts: dict[str, ConceptDiagnosis] = Field(
        default_factory=dict,
    )

    primary_concepts: list[str] = Field(
        default_factory=list,
    )

    weak_concepts: list[str] = Field(
        default_factory=list,
    )

    transfer_deficit_concepts: list[str] = Field(
        default_factory=list,
    )

    metadata: dict[str, object] = Field(
        default_factory=dict,
    )

    # ======================================================
    # Concept management
    # ======================================================

    def add_concept(
        self,
        diagnosis: ConceptDiagnosis,
    ) -> None:
        self.concepts[
            diagnosis.concept_id
        ] = diagnosis

    def get_concept(
        self,
        concept_id: str,
    ) -> ConceptDiagnosis | None:

        return self.concepts.get(
            concept_id,
        )

    # ======================================================
    # Inspection
    # ======================================================

    @property
    def concept_count(self) -> int:
        return len(self.concepts)

    @property
    def has_weakness(self) -> bool:
        return bool(
            self.weak_concepts
        )

    @property
    def has_transfer_deficit(self) -> bool:
        return bool(
            self.transfer_deficit_concepts
        )


class KnowledgeStateDiagnoser:
    """
    Deterministic knowledge-state diagnoser.

    Responsibilities
    ----------------
    - Inspect learner knowledge states.
    - Inspect historical evidence.
    - Calculate diagnostic signals.
    - Detect weak concepts.
    - Detect possible transfer deficits.
    - Never modify LearningState.
    - Never call an LLM.

    This is the domain diagnosis layer for the
    LongTutor knowledge-state diagnosis stage.
    """

    def __init__(
        self,
        weakness_threshold: float = 0.5,
        transfer_accuracy_threshold: float = 0.5,
    ) -> None:

        if not 0.0 <= weakness_threshold <= 1.0:
            raise ValueError(
                "weakness_threshold must be between 0 and 1."
            )

        if not 0.0 <= transfer_accuracy_threshold <= 1.0:
            raise ValueError(
                "transfer_accuracy_threshold must be between 0 and 1."
            )

        self._weakness_threshold = (
            weakness_threshold
        )

        self._transfer_accuracy_threshold = (
            transfer_accuracy_threshold
        )

    def diagnose(
        self,
        learning_state: LearningState,
        evidence: HistoricalEvidence,
        primary_concept_ids: list[str] | None = None,
    ) -> KnowledgeDiagnosis:
        """
        Diagnose the learner's current knowledge state.

        The diagnosis is derived from the learner state
        and selected historical evidence.
        """

        diagnosis = KnowledgeDiagnosis(
            learner_id=learning_state.learner_id,
            current_question=evidence.current_question,
        )

        primary_concepts = set(
            primary_concept_ids or []
        )

        evidence_concepts = set(
            evidence.related_concept_ids
        )

        concept_ids = (
            set(learning_state.knowledge.keys())
            | primary_concepts
            | evidence_concepts
        )

        for concept_id in sorted(
            concept_ids
        ):

            state = learning_state.get_knowledge_state(
                concept_id,
            )

            relevant_interactions = [
                interaction
                for interaction
                in evidence.relevant_interactions
                if concept_id
                in interaction.concept_ids
            ]

            recent_interactions = [
                interaction
                for interaction
                in evidence.recent_interactions
                if concept_id
                in interaction.concept_ids
            ]

            evidence_interactions = self._unique_interactions(
                relevant_interactions
                + recent_interactions
            )

            attempts = state.attempts

            correct_attempts = (
                state.correct_attempts
            )

            accuracy = (
                state.recent_accuracy
                if attempts > 0
                else 0.0
            )

            error_rate = state.error_rate

            evidence_count = len(
                evidence_interactions
            )

            has_recent_evidence = bool(
                recent_interactions
            )

            has_relevant_evidence = bool(
                relevant_interactions
            )

            weakness_signal = (
                state.mastery
                < self._weakness_threshold
                or (
                    attempts > 0
                    and accuracy
                    < self._weakness_threshold
                )
            )

            transfer_deficit_signal = (
                has_relevant_evidence
                and has_recent_evidence
                and accuracy
                < self._transfer_accuracy_threshold
            )

            concept_diagnosis = ConceptDiagnosis(
                concept_id=concept_id,
                mastery=state.mastery,
                level=state.level,
                attempts=attempts,
                correct_attempts=correct_attempts,
                accuracy=accuracy,
                error_rate=error_rate,
                evidence_count=evidence_count,
                has_recent_evidence=(
                    has_recent_evidence
                ),
                has_relevant_evidence=(
                    has_relevant_evidence
                ),
                weakness_signal=(
                    weakness_signal
                ),
                transfer_deficit_signal=(
                    transfer_deficit_signal
                ),
            )

            diagnosis.add_concept(
                concept_diagnosis,
            )

            if concept_id in primary_concepts:
                diagnosis.primary_concepts.append(
                    concept_id
                )

            if weakness_signal:
                diagnosis.weak_concepts.append(
                    concept_id
                )

            if transfer_deficit_signal:
                diagnosis.transfer_deficit_concepts.append(
                    concept_id
                )

        diagnosis.metadata.update(
            {
                "concept_count": (
                    diagnosis.concept_count
                ),
                "weak_concept_count": len(
                    diagnosis.weak_concepts
                ),
                "transfer_deficit_count": len(
                    diagnosis.transfer_deficit_concepts
                ),
                "weakness_threshold": (
                    self._weakness_threshold
                ),
                "transfer_accuracy_threshold": (
                    self._transfer_accuracy_threshold
                ),
            }
        )

        return diagnosis

    @staticmethod
    def _unique_interactions(
        interactions: list,
    ) -> list:

        result = []
        seen: set[str] = set()

        for interaction in interactions:

            if interaction.id in seen:
                continue

            seen.add(
                interaction.id
            )

            result.append(
                interaction
            )

        return result