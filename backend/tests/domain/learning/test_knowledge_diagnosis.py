from __future__ import annotations

from datetime import UTC, datetime, timedelta

from backend.domain.learning.historical_evidence import (
    HistoricalEvidence,
)
from backend.domain.learning.knowledge_diagnosis import (
    KnowledgeStateDiagnoser,
)
from backend.domain.learning.learning_interaction import (
    LearningInteraction,
)
from backend.domain.learning.learning_state import (
    LearningState,
)


def test_diagnosis_reads_current_knowledge_state():

    state = LearningState(
        learner_id="learner-1",
    )

    state.update_mastery(
        "python",
        0.5,
    )

    evidence = HistoricalEvidence(
        learner_id="learner-1",
        current_question="Explain Python functions.",
    )

    diagnosis = KnowledgeStateDiagnoser().diagnose(
        state,
        evidence,
        primary_concept_ids=[
            "python",
        ],
    )

    concept = diagnosis.get_concept(
        "python",
    )

    assert concept is not None

    assert concept.mastery == 0.5
    assert concept.level.value == "intermediate"

    assert diagnosis.primary_concepts == [
        "python",
    ]


def test_diagnosis_detects_weak_concept():

    state = LearningState(
        learner_id="learner-1",
    )

    state.update_mastery(
        "python",
        0.2,
    )

    evidence = HistoricalEvidence(
        learner_id="learner-1",
        current_question="Explain Python functions.",
    )

    diagnosis = KnowledgeStateDiagnoser().diagnose(
        state,
        evidence,
        primary_concept_ids=[
            "python",
        ],
    )

    assert (
        "python"
        in diagnosis.weak_concepts
    )

    assert diagnosis.has_weakness


def test_diagnosis_uses_historical_evidence():

    state = LearningState(
        learner_id="learner-1",
    )

    interaction = LearningInteraction(
        learner_id="learner-1",
        question_id="q1",
        question="What is a function?",
        answer="A reusable block.",
        correct=True,
        concept_ids=[
            "python",
        ],
    )

    state.interactions.append(
        interaction,
    )

    evidence = HistoricalEvidence(
        learner_id="learner-1",
        current_question="Explain Python functions.",
        relevant_interactions=[
            interaction,
        ],
        recent_interactions=[
            interaction,
        ],
        related_concept_ids=[
            "python",
        ],
    )

    diagnosis = KnowledgeStateDiagnoser().diagnose(
        state,
        evidence,
    )

    concept = diagnosis.get_concept(
        "python",
    )

    assert concept is not None

    assert concept.evidence_count == 1

    assert concept.has_recent_evidence

    assert concept.has_relevant_evidence


def test_diagnosis_does_not_modify_learning_state():

    state = LearningState(
        learner_id="learner-1",
    )

    state.update_mastery(
        "python",
        0.2,
    )

    before = state.model_dump(
        mode="json",
    )

    evidence = HistoricalEvidence(
        learner_id="learner-1",
        current_question="Explain Python.",
    )

    KnowledgeStateDiagnoser().diagnose(
        state,
        evidence,
        primary_concept_ids=[
            "python",
        ],
    )

    after = state.model_dump(
        mode="json",
    )

    assert after == before


def test_diagnosis_detects_transfer_deficit_signal():

    state = LearningState(
        learner_id="learner-1",
    )

    interaction = LearningInteraction(
        learner_id="learner-1",
        question_id="q1",
        question="Related problem",
        answer="Wrong answer",
        correct=False,
        concept_ids=[
            "recursion",
        ],
        timestamp=datetime.now(UTC),
    )

    state.interactions.append(
        interaction,
    )

    state.get_knowledge_state(
        "recursion",
    ).record_attempt(
        False,
    )

    evidence = HistoricalEvidence(
        learner_id="learner-1",
        current_question="New recursion problem.",
        relevant_interactions=[
            interaction,
        ],
        recent_interactions=[
            interaction,
        ],
        related_concept_ids=[
            "recursion",
        ],
    )

    diagnosis = KnowledgeStateDiagnoser().diagnose(
        state,
        evidence,
    )

    assert (
        "recursion"
        in diagnosis.transfer_deficit_concepts
    )

    assert diagnosis.has_transfer_deficit


def test_diagnosis_handles_unknown_concept():

    state = LearningState(
        learner_id="learner-1",
    )

    evidence = HistoricalEvidence(
        learner_id="learner-1",
        current_question="Explain recursion.",
    )

    diagnosis = KnowledgeStateDiagnoser().diagnose(
        state,
        evidence,
        primary_concept_ids=[
            "recursion",
        ],
    )

    concept = diagnosis.get_concept(
        "recursion",
    )

    assert concept is not None

    assert concept.mastery == 0.0
    assert concept.level.value == "unknown"

    assert (
        "recursion"
        in diagnosis.weak_concepts
    )