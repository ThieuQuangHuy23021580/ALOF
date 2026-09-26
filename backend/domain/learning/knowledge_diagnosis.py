from __future__ import annotations

from pydantic import BaseModel, Field

from backend.domain.knowledge.knowledge_level import (
    KnowledgeLevel,
)
from backend.domain.knowledge.knowledge_state import KnowledgeState
from backend.domain.learning.historical_evidence import (
    HistoricalEvidence,
)
from backend.domain.learning.learning_interaction import (
    LearningInteraction,
)
from backend.domain.learning.learning_state import (
    LearningState,
)
from backend.domain.learning.temporal_error_pattern import (
    TemporalErrorPattern,
    TemporalErrorPatternDetector,
)


class ConceptDiagnosis(BaseModel):
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

    retrieved_error_count: int = 0

    retrieved_correct_count: int = 0

    retrieved_accuracy: float = 0.0

    retrieved_error_rate: float = 0.0

    recent_error_count: int = 0

    relevant_error_count: int = 0

    evidence_confidence: float = 0.0


class KnowledgeDiagnosis(BaseModel):
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
    Deterministic adaptive knowledge-state diagnoser.

    Diagnosis combines:
    - persistent learner knowledge state;
    - retrieved historical evidence;
    - recent evidence;
    - relevant evidence;
    - retrieved correctness/error signals;
    - temporal error dynamics.

    Temporal dynamics detect:
    - persistent errors;
    - recovery;
    - unstable correctness;
    - recent error pressure.

    The same temporal signals are also used to rank
    adaptive quiz targets.

    The diagnoser never modifies LearningState
    and never calls an LLM.
    """

    def __init__(
        self,
        weakness_threshold: float = 0.5,
        transfer_accuracy_threshold: float = 0.5,
        confidence_k: float = 5.0,
        temporal_detector: (
            TemporalErrorPatternDetector | None
        ) = None,
    ) -> None:

        if not 0.0 <= weakness_threshold <= 1.0:
            raise ValueError(
                "weakness_threshold must be between 0 and 1."
            )

        if not 0.0 <= transfer_accuracy_threshold <= 1.0:
            raise ValueError(
                "transfer_accuracy_threshold must be between 0 and 1."
            )

        if confidence_k <= 0.0:
            raise ValueError(
                "confidence_k must be greater than 0."
            )

        self._weakness_threshold = (
            weakness_threshold
        )

        self._transfer_accuracy_threshold = (
            transfer_accuracy_threshold
        )

        self._confidence_k = confidence_k

        self._temporal_detector = (
            temporal_detector
            if temporal_detector is not None
            else TemporalErrorPatternDetector(
                confidence_k=confidence_k,
            )
        )

    def diagnose(
        self,
        learning_state: LearningState,
        evidence: HistoricalEvidence,
        primary_concept_ids: list[str] | None = None,
    ) -> KnowledgeDiagnosis:

        diagnosis = KnowledgeDiagnosis(
            learner_id=learning_state.learner_id,
            current_question=evidence.current_question,
        )

        primary_concepts = {
            str(value)
            for value in (
                primary_concept_ids or []
            )
            if value is not None
        }

        evidence_concepts = {
            str(value)
            for value in evidence.related_concept_ids
            if value is not None
        }

        concept_ids = (
            {
                str(value)
                for value in learning_state.knowledge.keys()
            }
            | primary_concepts
            | evidence_concepts
        )

        temporal_patterns: dict[
            str,
            TemporalErrorPattern,
        ] = {}

        target_scores: dict[
            str,
            float,
        ] = {}

        for concept_id in sorted(
            concept_ids
        ):

            state = learning_state.knowledge.get(
                concept_id
            )

            if state is None:
                state = KnowledgeState(
                    concept_id=concept_id
                )

            relevant_interactions = [
                interaction
                for interaction in evidence.relevant_interactions
                if concept_id
                in {
                    str(value)
                    for value in interaction.concept_ids
                }
            ]

            recent_interactions = [
                interaction
                for interaction in evidence.recent_interactions
                if concept_id
                in {
                    str(value)
                    for value in interaction.concept_ids
                }
            ]

            related_interactions = [
                interaction
                for interaction in evidence.related_interactions
                if concept_id
                in {
                    str(value)
                    for value in interaction.concept_ids
                }
            ]

            retrieved_interactions = (
                self._unique_interactions(
                    relevant_interactions
                    + related_interactions
                    + recent_interactions
                )
            )

            retrieved_errors = [
                interaction
                for interaction in retrieved_interactions
                if interaction.correct is False
            ]

            retrieved_correct = [
                interaction
                for interaction in retrieved_interactions
                if interaction.correct is True
            ]

            recent_errors = [
                interaction
                for interaction in recent_interactions
                if interaction.correct is False
            ]

            relevant_errors = [
                interaction
                for interaction in relevant_interactions
                if interaction.correct is False
            ]

            evidence_count = len(
                retrieved_interactions
            )

            retrieved_correct_count = len(
                retrieved_correct
            )

            retrieved_error_count = len(
                retrieved_errors
            )

            observed_attempts = (
                retrieved_correct_count
                + retrieved_error_count
            )

            retrieved_accuracy = (
                retrieved_correct_count
                / observed_attempts
                if observed_attempts > 0
                else 0.0
            )

            retrieved_error_rate = (
                retrieved_error_count
                / observed_attempts
                if observed_attempts > 0
                else 0.0
            )

            attempts = state.attempts

            correct_attempts = (
                state.correct_attempts
            )

            base_accuracy = (
                state.recent_accuracy
                if attempts > 0
                else 0.0
            )

            error_rate = state.error_rate

            has_recent_evidence = bool(
                recent_interactions
            )

            has_relevant_evidence = bool(
                relevant_interactions
            )

            evidence_confidence = (
                self._evidence_confidence(
                    observed_attempts,
                )
            )

            effective_accuracy = (
                self._combine_accuracy(
                    base_accuracy=base_accuracy,
                    retrieved_accuracy=retrieved_accuracy,
                    evidence_confidence=evidence_confidence,
                    observed_attempts=observed_attempts,
                )
            )

            effective_error_rate = (
                self._combine_error_rate(
                    base_error_rate=error_rate,
                    retrieved_error_rate=retrieved_error_rate,
                    evidence_confidence=evidence_confidence,
                    observed_attempts=observed_attempts,
                )
            )

            temporal_pattern = (
                self._temporal_detector.detect(
                    concept_id=concept_id,
                    interactions=learning_state.interactions,
                )
            )

            temporal_patterns[
                concept_id
            ] = temporal_pattern

            weakness_signal = (
                self._weakness_signal(
                    mastery=state.mastery,
                    base_accuracy=base_accuracy,
                    effective_accuracy=effective_accuracy,
                    retrieved_error_rate=retrieved_error_rate,
                    observed_attempts=observed_attempts,
                    temporal_pattern=temporal_pattern,
                )
            )

            transfer_deficit_signal = (
                self._transfer_deficit_signal(
                    has_relevant_evidence=(
                        has_relevant_evidence
                    ),
                    has_recent_evidence=(
                        has_recent_evidence
                    ),
                    effective_accuracy=(
                        effective_accuracy
                    ),
                    retrieved_error_count=(
                        retrieved_error_count
                    ),
                )
            )

            concept_diagnosis = ConceptDiagnosis(
                concept_id=concept_id,
                mastery=state.mastery,
                level=state.level,
                attempts=attempts,
                correct_attempts=correct_attempts,
                accuracy=effective_accuracy,
                error_rate=effective_error_rate,
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
                retrieved_error_count=(
                    retrieved_error_count
                ),
                retrieved_correct_count=(
                    retrieved_correct_count
                ),
                retrieved_accuracy=(
                    retrieved_accuracy
                ),
                retrieved_error_rate=(
                    retrieved_error_rate
                ),
                recent_error_count=len(
                    recent_errors
                ),
                relevant_error_count=len(
                    relevant_errors
                ),
                evidence_confidence=(
                    evidence_confidence
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

            target_scores[
                concept_id
            ] = self._adaptive_quiz_target_score(
                diagnosis=concept_diagnosis,
                temporal_pattern=temporal_pattern,
                is_primary=(
                    concept_id in primary_concepts
                ),
                is_transfer_deficit=(
                    transfer_deficit_signal
                ),
            )

        diagnosis.weak_concepts.sort(
            key=lambda concept_id: (
                -target_scores.get(
                    concept_id,
                    0.0,
                ),
                concept_id,
            )
        )

        diagnosis.transfer_deficit_concepts.sort(
            key=lambda concept_id: (
                -target_scores.get(
                    concept_id,
                    0.0,
                ),
                concept_id,
            )
        )

        adaptive_quiz_targets = sorted(
            target_scores.items(),
            key=lambda item: (
                -item[1],
                item[0],
            ),
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
                "confidence_k": (
                    self._confidence_k
                ),
                "adaptive_evidence_used": (
                    evidence.has_evidence
                ),
                "retrieved_interaction_count": (
                    evidence.interaction_count
                ),
                "temporal_error_patterns": {
                    concept_id: pattern.as_dict()
                    for concept_id, pattern
                    in temporal_patterns.items()
                },
                "adaptive_quiz_targets": [
                    {
                        "concept_id": concept_id,
                        "score": score,
                    }
                    for concept_id, score
                    in adaptive_quiz_targets
                ],
            }
        )

        return diagnosis

    def _adaptive_quiz_target_score(
        self,
        diagnosis: ConceptDiagnosis,
        temporal_pattern: TemporalErrorPattern,
        is_primary: bool,
        is_transfer_deficit: bool,
    ) -> float:
        """
        Rank concepts for the next adaptive quiz.

        Higher score means stronger evidence that the concept
        should be revisited.

        The score combines:
        - current weakness;
        - temporal persistence;
        - instability;
        - recent error pressure;
        - transfer deficit;
        - low effective accuracy;
        - uncertainty;
        - recovery penalty.

        Recovery reduces priority so that a learner who is
        already demonstrating sustained recovery is not
        repeatedly targeted at the same rate.
        """

        weakness = (
            1.0
            - max(
                0.0,
                min(
                    1.0,
                    diagnosis.mastery,
                ),
            )
        )

        accuracy_gap = (
            1.0
            - max(
                0.0,
                min(
                    1.0,
                    diagnosis.accuracy,
                ),
            )
        )

        persistence = (
            temporal_pattern.persistence_score
        )

        instability = (
            temporal_pattern.instability_score
        )

        recent_error = (
            temporal_pattern.recent_error_pressure
        )

        recovery = (
            temporal_pattern.recovery_score
        )

        transfer = (
            1.0
            if is_transfer_deficit
            else 0.0
        )

        uncertainty = (
            1.0
            - max(
                0.0,
                min(
                    1.0,
                    diagnosis.evidence_confidence,
                ),
            )
        )

        primary_bonus = (
            0.05
            if is_primary
            else 0.0
        )

        raw_score = (
            0.25 * weakness
            + 0.20 * accuracy_gap
            + 0.20 * persistence
            + 0.15 * instability
            + 0.10 * recent_error
            + 0.10 * transfer
            + 0.05 * uncertainty
            + primary_bonus
            - 0.15 * recovery
        )

        return max(
            0.0,
            min(
                1.0,
                raw_score,
            ),
        )

    def _weakness_signal(
        self,
        mastery: float,
        base_accuracy: float,
        effective_accuracy: float,
        retrieved_error_rate: float,
        observed_attempts: int,
        temporal_pattern: TemporalErrorPattern,
    ) -> bool:

        if mastery < self._weakness_threshold:
            return True

        if (
            observed_attempts > 0
            and effective_accuracy
            < self._weakness_threshold
        ):
            return True

        if (
            observed_attempts > 0
            and retrieved_error_rate
            >= self._weakness_threshold
        ):
            return True

        if (
            base_accuracy < self._weakness_threshold
            and observed_attempts > 0
        ):
            return True

        if self._temporal_weakness_signal(
            temporal_pattern
        ):
            return True

        return False

    @staticmethod
    def _temporal_weakness_signal(
        pattern: TemporalErrorPattern,
    ) -> bool:

        if pattern.confidence < 0.35:
            return False

        if pattern.pattern == "persistent":
            return (
                pattern.persistence_score
                >= 0.60
            )

        if pattern.pattern == "unstable":
            return (
                pattern.recent_error_pressure
                >= 0.50
                and pattern.instability_score
                >= 0.65
            )

        return False

    def _transfer_deficit_signal(
        self,
        has_relevant_evidence: bool,
        has_recent_evidence: bool,
        effective_accuracy: float,
        retrieved_error_count: int,
    ) -> bool:

        if not has_relevant_evidence:
            return False

        if not has_recent_evidence:
            return False

        if retrieved_error_count <= 0:
            return False

        return (
            effective_accuracy
            < self._transfer_accuracy_threshold
        )

    def _evidence_confidence(
        self,
        observed_attempts: int,
    ) -> float:

        if observed_attempts <= 0:
            return 0.0

        return (
            observed_attempts
            / (
                observed_attempts
                + self._confidence_k
            )
        )

    @staticmethod
    def _combine_accuracy(
        base_accuracy: float,
        retrieved_accuracy: float,
        evidence_confidence: float,
        observed_attempts: int,
    ) -> float:

        if observed_attempts <= 0:
            return base_accuracy

        combined = (
            (
                1.0 - evidence_confidence
            )
            * base_accuracy
            + evidence_confidence
            * retrieved_accuracy
        )

        return max(
            0.0,
            min(
                1.0,
                combined,
            ),
        )

    @staticmethod
    def _combine_error_rate(
        base_error_rate: float,
        retrieved_error_rate: float,
        evidence_confidence: float,
        observed_attempts: int,
    ) -> float:

        if observed_attempts <= 0:
            return base_error_rate

        combined = (
            (
                1.0 - evidence_confidence
            )
            * base_error_rate
            + evidence_confidence
            * retrieved_error_rate
        )

        return max(
            0.0,
            min(
                1.0,
                combined,
            ),
        )

    @staticmethod
    def _unique_interactions(
        interactions: list[
            LearningInteraction
        ],
    ) -> list[
        LearningInteraction
    ]:

        result: list[
            LearningInteraction
        ] = []

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