from __future__ import annotations

from backend.domain.learning.historical_evidence import (
    HistoricalEvidence,
)
from backend.domain.learning.learning_interaction import (
    LearningInteraction,
)


def test_historical_evidence_defaults():

    evidence = HistoricalEvidence(
        learner_id="learner-1",
    )

    assert (
        evidence.learner_id
        == "learner-1"
    )

    assert (
        evidence.current_question
        == ""
    )

    assert (
        evidence.relevant_interactions
        == []
    )

    assert (
        evidence.recent_interactions
        == []
    )

    assert (
        evidence.related_concept_ids
        == []
    )

    assert (
        evidence.metadata
        == {}
    )

    assert (
        evidence.has_evidence
        is False
    )

    assert (
        evidence.interaction_count
        == 0
    )


def test_historical_evidence_stores_current_question():

    evidence = HistoricalEvidence(
        learner_id="learner-1",
        current_question=(
            "How many cuts are needed?"
        ),
    )

    assert (
        evidence.current_question
        == "How many cuts are needed?"
    )


def test_historical_evidence_adds_relevant_interaction():

    interaction = LearningInteraction(
        learner_id="learner-1",
        question_id="q-1",
        question="How many cuts are needed?",
        answer="4",
        correct=True,
        concept_ids=[
            "interval_logic",
        ],
    )

    evidence = HistoricalEvidence(
        learner_id="learner-1",
    )

    evidence.add_relevant_interaction(
        interaction,
    )

    assert (
        evidence.relevant_interactions
        == [interaction]
    )

    assert (
        evidence.interaction_count
        == 1
    )

    assert (
        evidence.has_evidence
        is True
    )


def test_historical_evidence_adds_recent_interaction():

    interaction = LearningInteraction(
        learner_id="learner-1",
        question_id="q-2",
        question="What is 5 - 1?",
        answer="4",
        correct=False,
        concept_ids=[
            "interval_logic",
        ],
    )

    evidence = HistoricalEvidence(
        learner_id="learner-1",
    )

    evidence.add_recent_interaction(
        interaction,
    )

    assert (
        evidence.recent_interactions
        == [interaction]
    )

    assert (
        evidence.interaction_count
        == 1
    )

    assert (
        evidence.has_evidence
        is True
    )


def test_historical_evidence_adds_related_concepts():

    evidence = HistoricalEvidence(
        learner_id="learner-1",
    )

    evidence.add_related_concept(
        "interval_logic",
    )

    evidence.add_related_concept(
        "interval_applications",
    )

    assert (
        evidence.related_concept_ids
        == [
            "interval_logic",
            "interval_applications",
        ]
    )


def test_historical_evidence_does_not_duplicate_concepts():

    evidence = HistoricalEvidence(
        learner_id="learner-1",
    )

    evidence.add_related_concept(
        "interval_logic",
    )

    evidence.add_related_concept(
        "interval_logic",
    )

    assert (
        evidence.related_concept_ids
        == [
            "interval_logic",
        ]
    )


def test_historical_evidence_metadata():

    evidence = HistoricalEvidence(
        learner_id="learner-1",
    )

    evidence.set_metadata(
        "source",
        "longtutor_history",
    )

    evidence.set_metadata(
        "selection_strategy",
        "related_concept",
    )

    assert (
        evidence.get_metadata(
            "source",
        )
        == "longtutor_history"
    )

    assert (
        evidence.get_metadata(
            "selection_strategy",
        )
        == "related_concept"
    )

    assert (
        evidence.get_metadata(
            "unknown",
        )
        is None
    )


def test_historical_evidence_keeps_relevant_and_recent_history_separate():

    relevant = LearningInteraction(
        learner_id="learner-1",
        question_id="q-1",
        question="Previous related problem",
        answer="4",
        correct=True,
        concept_ids=[
            "interval_logic",
        ],
    )

    recent = LearningInteraction(
        learner_id="learner-1",
        question_id="q-2",
        question="Recent problem",
        answer="5",
        correct=False,
        concept_ids=[
            "interval_applications",
        ],
    )

    evidence = HistoricalEvidence(
        learner_id="learner-1",
    )

    evidence.add_relevant_interaction(
        relevant,
    )

    evidence.add_recent_interaction(
        recent,
    )

    assert (
        evidence.relevant_interactions
        == [relevant]
    )

    assert (
        evidence.recent_interactions
        == [recent]
    )

    assert (
        evidence.interaction_count
        == 2
    )


def test_historical_evidence_isolated_between_instances():

    first = HistoricalEvidence(
        learner_id="learner-1",
    )

    second = HistoricalEvidence(
        learner_id="learner-2",
    )

    interaction = LearningInteraction(
        learner_id="learner-1",
        question_id="q-1",
        question="Question",
        answer="Answer",
        correct=True,
    )

    first.add_recent_interaction(
        interaction,
    )

    first.add_related_concept(
        "python",
    )

    assert (
        second.recent_interactions
        == []
    )

    assert (
        second.related_concept_ids
        == []
    )

    assert (
        second.has_evidence
        is False
    )