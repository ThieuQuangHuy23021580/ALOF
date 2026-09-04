from __future__ import annotations

from datetime import UTC, datetime

from backend.domain.learning.historical_evidence_builder import (
    HistoricalEvidenceBuilder,
)
from backend.domain.learning.learning_interaction import (
    LearningInteraction,
)
from backend.domain.learning.learning_state import (
    LearningState,
)


def test_builder_includes_external_history():
    state = LearningState(
        learner_id="student-1",
    )

    interaction = LearningInteraction(
        learner_id="student-1",
        question_id="q-native",
        question="Native question",
        answer="42",
        correct=True,
        concept_ids=["algebra"],
        timestamp=datetime(
            2026,
            1,
            1,
            tzinfo=UTC,
        ),
    )

    state.add_interaction(interaction)

    history_info = [
        {
            "question_id": "q-history",
            "question": "What is x + 2 = 5?",
            "answer": "3",
            "correct": True,
            "concept_ids": ["algebra"],
            "timestamp": "2026-01-02T10:00:00Z",
        }
    ]

    related_history = [
        {
            "question_id": "q-related",
            "question": "Solve 2x = 10",
            "answer": "5",
            "correct": True,
            "concept_ids": ["equation"],
            "timestamp": "2026-01-03T10:00:00Z",
        }
    ]

    builder = HistoricalEvidenceBuilder()

    evidence = builder.build(
        learning_state=state,
        current_question="Solve x + 2 = 5",
        related_concept_ids=["algebra"],
        history_info=history_info,
        related_history=related_history,
    )

    assert evidence.learner_id == "student-1"

    assert evidence.has_evidence

    assert evidence.get_metadata(
        "external_history_count"
    ) == 1

    assert evidence.get_metadata(
        "external_related_history_count"
    ) == 1

    assert evidence.get_metadata(
        "external_evidence_count"
    ) == 2

    relevant_questions = [
        interaction.question
        for interaction in evidence.relevant_interactions
    ]

    related_questions = [
        interaction.question
        for interaction in evidence.related_interactions
    ]

    assert "What is x + 2 = 5?" in relevant_questions
    assert "Solve 2x = 10" in related_questions


def test_builder_normalizes_external_history_to_learning_interaction():
    state = LearningState(
        learner_id="student-1",
    )

    history_info = [
        {
            "qid": 152,
            "content": "下图中有个平行四边形．",
            "student_answer": "平行四边形",
            "is_correct": True,
            "conceptIds": ["parallel"],
            "createdAt": "2021-05-22T10:07:35Z",
        }
    ]

    builder = HistoricalEvidenceBuilder()

    evidence = builder.build(
        learning_state=state,
        current_question="平行四边形是什么？",
        related_concept_ids=["parallel"],
        history_info=history_info,
    )

    assert len(evidence.relevant_interactions) == 1

    interaction = evidence.relevant_interactions[0]

    assert isinstance(
        interaction,
        LearningInteraction,
    )

    assert interaction.learner_id == "student-1"
    assert interaction.question_id == "152"
    assert interaction.question == "下图中有个平行四边形．"
    assert interaction.answer == "平行四边形"
    assert interaction.correct is True
    assert interaction.concept_ids == ["parallel"]


def test_builder_does_not_propagate_gold_fields():
    state = LearningState(
        learner_id="student-1",
    )

    history_info = [
        {
            "question_id": "q1",
            "question": "What is 1 + 1?",
            "answer": "2",
            "correct": True,
            "concept_ids": ["arithmetic"],
            "gold_memory_queries": [
                {
                    "query": "What did the student answer?",
                    "answer": "2",
                }
            ],
            "gold_answer": "2",
            "gold_answers": ["2"],
        }
    ]

    builder = HistoricalEvidenceBuilder()

    evidence = builder.build(
        learning_state=state,
        current_question="What is 1 + 1?",
        related_concept_ids=["arithmetic"],
        history_info=history_info,
    )

    assert len(evidence.relevant_interactions) == 1

    interaction = evidence.relevant_interactions[0]

    assert "gold_memory_queries" not in interaction.metadata
    assert "gold_answer" not in interaction.metadata
    assert "gold_answers" not in interaction.metadata


def test_builder_keeps_native_learning_state_evidence():
    state = LearningState(
        learner_id="student-1",
    )

    interaction = LearningInteraction(
        learner_id="student-1",
        question_id="native-q1",
        question="Solve x + 1 = 2",
        answer="1",
        correct=True,
        concept_ids=["algebra"],
        timestamp=datetime(
            2026,
            1,
            1,
            tzinfo=UTC,
        ),
    )

    state.add_interaction(interaction)

    builder = HistoricalEvidenceBuilder()

    evidence = builder.build(
        learning_state=state,
        current_question="Solve x + 1 = 2",
        related_concept_ids=["algebra"],
    )

    assert len(
        evidence.recent_interactions
    ) == 1

    assert (
        evidence.recent_interactions[0].question_id
        == "native-q1"
    )

    assert evidence.get_metadata(
        "source_interaction_count"
    ) == 1