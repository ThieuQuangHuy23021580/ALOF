from __future__ import annotations

from datetime import UTC, datetime, timedelta

from backend.domain.learning.historical_evidence_builder import (
    HistoricalEvidenceBuilder,
)
from backend.domain.learning.learning_interaction import (
    LearningInteraction,
)
from backend.domain.learning.learning_state import (
    LearningState,
)


def _interaction(
    learner_id: str,
    question_id: str,
    concept_ids: list[str],
    days_ago: int,
    correct: bool | None = True,
) -> LearningInteraction:

    return LearningInteraction(
        learner_id=learner_id,
        question_id=question_id,
        question=f"Question {question_id}",
        answer="Answer",
        correct=correct,
        concept_ids=concept_ids,
        timestamp=(
            datetime.now(UTC)
            - timedelta(days=days_ago)
        ),
    )


def test_builder_creates_empty_evidence():

    state = LearningState(
        learner_id="learner-1",
    )

    builder = HistoricalEvidenceBuilder()

    evidence = builder.build(
        learning_state=state,
        current_question="Current question",
    )

    assert (
        evidence.learner_id
        == "learner-1"
    )

    assert (
        evidence.current_question
        == "Current question"
    )

    assert (
        evidence.recent_interactions
        == []
    )

    assert (
        evidence.relevant_interactions
        == []
    )

    assert (
        evidence.has_evidence
        is False
    )


def test_builder_selects_recent_interactions():

    state = LearningState(
        learner_id="learner-1",
    )

    for index in range(7):

        state.interactions.append(
            _interaction(
                learner_id="learner-1",
                question_id=f"q-{index}",
                concept_ids=[
                    "python",
                ],
                days_ago=7 - index,
            )
        )

    builder = HistoricalEvidenceBuilder(
        recent_limit=3,
    )

    evidence = builder.build(
        learning_state=state,
    )

    assert len(
        evidence.recent_interactions
    ) == 3

    assert [
        interaction.question_id
        for interaction
        in evidence.recent_interactions
    ] == [
        "q-4",
        "q-5",
        "q-6",
    ]


def test_builder_selects_relevant_interactions():

    state = LearningState(
        learner_id="learner-1",
    )

    related = _interaction(
        learner_id="learner-1",
        question_id="q-python",
        concept_ids=[
            "python",
            "functions",
        ],
        days_ago=10,
    )

    unrelated = _interaction(
        learner_id="learner-1",
        question_id="q-math",
        concept_ids=[
            "algebra",
        ],
        days_ago=2,
    )

    state.interactions.extend(
        [
            related,
            unrelated,
        ]
    )

    builder = HistoricalEvidenceBuilder()

    evidence = builder.build(
        learning_state=state,
        current_question="Explain Python functions.",
        related_concept_ids=[
            "functions",
        ],
    )

    assert (
        evidence.relevant_interactions
        == [related]
    )

    assert (
        unrelated
        not in evidence.relevant_interactions
    )


def test_builder_collects_related_concepts():

    state = LearningState(
        learner_id="learner-1",
    )

    state.interactions.append(
        _interaction(
            learner_id="learner-1",
            question_id="q-1",
            concept_ids=[
                "python",
                "functions",
            ],
            days_ago=1,
        )
    )

    builder = HistoricalEvidenceBuilder()

    evidence = builder.build(
        learning_state=state,
    )

    assert (
        evidence.related_concept_ids
        == [
            "python",
            "functions",
        ]
    )


def test_builder_does_not_duplicate_related_concepts():

    state = LearningState(
        learner_id="learner-1",
    )

    state.interactions.extend(
        [
            _interaction(
                learner_id="learner-1",
                question_id="q-1",
                concept_ids=[
                    "python",
                    "functions",
                ],
                days_ago=2,
            ),
            _interaction(
                learner_id="learner-1",
                question_id="q-2",
                concept_ids=[
                    "python",
                    "loops",
                ],
                days_ago=1,
            ),
        ]
    )

    builder = HistoricalEvidenceBuilder()

    evidence = builder.build(
        learning_state=state,
    )

    assert (
        evidence.related_concept_ids
        == [
            "python",
            "functions",
            "loops",
        ]
    )


def test_builder_metadata():

    state = LearningState(
        learner_id="learner-1",
    )

    state.interactions.append(
        _interaction(
            learner_id="learner-1",
            question_id="q-1",
            concept_ids=[
                "python",
            ],
            days_ago=1,
        )
    )

    builder = HistoricalEvidenceBuilder(
        recent_limit=5,
    )

    evidence = builder.build(
        learning_state=state,
    )

    assert (
        evidence.get_metadata(
            "selection_strategy",
        )
        == "recent_and_related_concepts"
    )

    assert (
        evidence.get_metadata(
            "recent_limit",
        )
        == 5
    )

    assert (
        evidence.get_metadata(
            "source_interaction_count",
        )
        == 1
    )

    assert (
        evidence.get_metadata(
            "recent_interaction_count",
        )
        == 1
    )


def test_builder_handles_related_concepts_without_history():

    state = LearningState(
        learner_id="learner-1",
    )

    builder = HistoricalEvidenceBuilder()

    evidence = builder.build(
        learning_state=state,
        current_question="Python functions",
        related_concept_ids=[
            "functions",
        ],
    )

    assert (
        evidence.current_question
        == "Python functions"
    )

    assert (
        evidence.related_concept_ids
        == []
    )

    assert (
        evidence.has_evidence
        is False
    )


def test_builder_is_deterministic():

    state = LearningState(
        learner_id="learner-1",
    )

    state.interactions.extend(
        [
            _interaction(
                learner_id="learner-1",
                question_id="q-1",
                concept_ids=[
                    "python",
                ],
                days_ago=3,
            ),
            _interaction(
                learner_id="learner-1",
                question_id="q-2",
                concept_ids=[
                    "functions",
                ],
                days_ago=2,
            ),
            _interaction(
                learner_id="learner-1",
                question_id="q-3",
                concept_ids=[
                    "python",
                ],
                days_ago=1,
            ),
        ]
    )

    builder = HistoricalEvidenceBuilder(
        recent_limit=2,
    )

    first = builder.build(
        learning_state=state,
    )

    second = builder.build(
        learning_state=state,
    )

    assert (
        first.model_dump()
        == second.model_dump()
    )