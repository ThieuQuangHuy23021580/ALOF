from __future__ import annotations

from datetime import UTC, datetime, timedelta

from backend.application.orchestration.adaptive_learning_pipeline import (
    AdaptiveLearningPipeline,
)
from backend.domain.learning.learning_interaction import (
    LearningInteraction,
)
from backend.domain.learning.learning_state import (
    LearningState,
)
from backend.domain.learning.knowledge_diagnosis import (
    KnowledgeStateDiagnoser,
)
from backend.domain.learning.historical_evidence_builder import (
    HistoricalEvidenceBuilder,
)
from backend.domain.learning.adaptive_teaching_action import (
    AdaptiveTeachingActionSelector,
    TeachingActionType,
    TeachingStrategy,
)


def _interaction(
    *,
    interaction_id: str,
    concept_ids: list[str],
    correct: bool,
    timestamp: datetime,
) -> LearningInteraction:

    return LearningInteraction(
        id=interaction_id,
        learner_id="learner-1",
        question_id=interaction_id,
        question=f"Question {interaction_id}",
        answer="Answer",
        correct=correct,
        concept_ids=concept_ids,
        timestamp=timestamp,
    )


def test_adaptive_learning_pipeline_builds_complete_result():

    now = datetime.now(UTC)

    state = LearningState(
        learner_id="learner-1",
    )

    state.update_mastery(
        "interval_logic",
        0.2,
    )

    state.interactions.extend(
        [
            _interaction(
                interaction_id="interaction-1",
                concept_ids=["interval_logic"],
                correct=True,
                timestamp=now - timedelta(days=10),
            ),
            _interaction(
                interaction_id="interaction-2",
                concept_ids=["interval_logic"],
                correct=False,
                timestamp=now - timedelta(days=1),
            ),
        ]
    )

    pipeline = AdaptiveLearningPipeline()

    result = pipeline.run(
        learning_state=state,
        current_question=(
            "Một học sinh đi từ tầng 1 đến tầng 5. "
            "Có bao nhiêu khoảng cầu thang?"
        ),
        related_concept_ids=[
            "interval_logic",
        ],
        primary_concept_ids=[
            "interval_logic",
        ],
    )

    assert result is not None

    assert result.evidence is not None
    assert result.diagnosis is not None
    assert result.teaching_action is not None

    assert (
        result.evidence.learner_id
        == "learner-1"
    )

    assert (
        result.evidence.current_question
        != ""
    )

    assert (
        result.diagnosis.learner_id
        == "learner-1"
    )

    assert (
        "interval_logic"
        in result.diagnosis.concepts
    )

    assert (
        result.teaching_action.has_focus
    )

    assert (
        "interval_logic"
        in result.teaching_action.focus_concepts
    )


def test_pipeline_detects_recent_and_relevant_evidence():

    now = datetime.now(UTC)

    state = LearningState(
        learner_id="learner-1",
    )

    state.interactions.extend(
        [
            _interaction(
                interaction_id="old-related",
                concept_ids=["interval_logic"],
                correct=True,
                timestamp=now - timedelta(days=30),
            ),
            _interaction(
                interaction_id="recent-related",
                concept_ids=["interval_logic"],
                correct=False,
                timestamp=now - timedelta(days=1),
            ),
            _interaction(
                interaction_id="recent-unrelated",
                concept_ids=["fractions"],
                correct=True,
                timestamp=now,
            ),
        ]
    )

    pipeline = AdaptiveLearningPipeline()

    result = pipeline.run(
        learning_state=state,
        current_question="Solve an interval problem.",
        related_concept_ids=[
            "interval_logic",
        ],
        primary_concept_ids=[
            "interval_logic",
        ],
    )

    evidence = result.evidence

    assert (
        evidence.interaction_count
        > 0
    )

    assert (
        "interval_logic"
        in evidence.related_concept_ids
    )

    assert any(
        interaction.id == "recent-related"
        for interaction
        in evidence.recent_interactions
    )

    assert any(
        interaction.id == "old-related"
        for interaction
        in evidence.relevant_interactions
    )


def test_pipeline_detects_weak_knowledge():

    state = LearningState(
        learner_id="learner-1",
    )

    state.update_mastery(
        "python",
        0.2,
    )

    pipeline = AdaptiveLearningPipeline()

    result = pipeline.run(
        learning_state=state,
        current_question="Explain Python functions.",
        related_concept_ids=[
            "python",
        ],
        primary_concept_ids=[
            "python",
        ],
    )

    diagnosis = result.diagnosis

    assert (
        "python"
        in diagnosis.concepts
    )

    assert (
        "python"
        in diagnosis.weak_concepts
    )

    action = result.teaching_action

    assert (
        action.action
        == TeachingActionType.EXPLAIN
    )

    assert (
        action.strategy
        == TeachingStrategy.GUIDED_EXPLANATION
    )

    assert (
        "python"
        in action.focus_concepts
    )


def test_pipeline_detects_transfer_deficit():

    now = datetime.now(UTC)

    state = LearningState(
        learner_id="learner-1",
    )

    state.update_mastery(
        "interval_logic",
        0.6,
    )

    state.interactions.extend(
        [
            _interaction(
                interaction_id="relevant-1",
                concept_ids=["interval_logic"],
                correct=False,
                timestamp=now - timedelta(days=5),
            ),
            _interaction(
                interaction_id="recent-1",
                concept_ids=["interval_logic"],
                correct=False,
                timestamp=now - timedelta(days=1),
            ),
        ]
    )

    pipeline = AdaptiveLearningPipeline(
        diagnoser=KnowledgeStateDiagnoser(
            weakness_threshold=0.4,
            transfer_accuracy_threshold=0.5,
        ),
    )

    result = pipeline.run(
        learning_state=state,
        current_question="Solve an isomorphic interval problem.",
        related_concept_ids=[
            "interval_logic",
        ],
        primary_concept_ids=[
            "interval_logic",
        ],
    )

    diagnosis = result.diagnosis

    assert (
        "interval_logic"
        in diagnosis.transfer_deficit_concepts
    )

    action = result.teaching_action

    assert (
        action.action
        == TeachingActionType.SCAFFOLD
    )

    assert (
        action.strategy
        == TeachingStrategy.STEP_BY_STEP
    )

    assert (
        "interval_logic"
        in action.focus_concepts
    )


def test_pipeline_does_not_modify_learning_state():

    now = datetime.now(UTC)

    state = LearningState(
        learner_id="learner-1",
    )

    state.update_mastery(
        "python",
        0.2,
    )

    state.interactions.append(
        _interaction(
            interaction_id="interaction-1",
            concept_ids=["python"],
            correct=False,
            timestamp=now,
        )
    )

    original_mastery = (
        state.knowledge[
            "python"
        ].mastery
    )

    original_interaction_count = (
        len(
            state.interactions
        )
    )

    pipeline = AdaptiveLearningPipeline()

    pipeline.run(
        learning_state=state,
        current_question="Explain Python.",
        related_concept_ids=[
            "python",
        ],
        primary_concept_ids=[
            "python",
        ],
    )

    assert (
        state.knowledge[
            "python"
        ].mastery
        == original_mastery
    )

    assert (
        len(
            state.interactions
        )
        == original_interaction_count
    )


def test_pipeline_uses_injected_components():

    evidence_builder = HistoricalEvidenceBuilder(
        recent_limit=2,
    )

    diagnoser = KnowledgeStateDiagnoser(
        weakness_threshold=0.5,
        transfer_accuracy_threshold=0.5,
    )

    action_selector = AdaptiveTeachingActionSelector(
        weak_mastery_threshold=0.4,
        strong_mastery_threshold=0.7,
    )

    pipeline = AdaptiveLearningPipeline(
        evidence_builder=evidence_builder,
        diagnoser=diagnoser,
        action_selector=action_selector,
    )

    state = LearningState(
        learner_id="learner-1",
    )

    state.update_mastery(
        "python",
        0.2,
    )

    result = pipeline.run(
        learning_state=state,
        current_question="Explain Python.",
        related_concept_ids=[
            "python",
        ],
        primary_concept_ids=[
            "python",
        ],
    )

    assert result.evidence is not None
    assert result.diagnosis is not None
    assert result.teaching_action is not None

    assert (
        result.evidence.metadata[
            "recent_limit"
        ]
        == 2
    )


def test_pipeline_handles_empty_learning_state():

    state = LearningState(
        learner_id="new-learner",
    )

    pipeline = AdaptiveLearningPipeline()

    result = pipeline.run(
        learning_state=state,
        current_question="Explain fractions.",
        related_concept_ids=[
            "fractions",
        ],
        primary_concept_ids=[
            "fractions",
        ],
    )

    assert (
        result.evidence.learner_id
        == "new-learner"
    )

    assert (
        result.diagnosis.learner_id
        == "new-learner"
    )

    assert (
        "fractions"
        in result.diagnosis.concepts
    )

    assert (
        result.teaching_action.action
        == TeachingActionType.EXPLAIN
    )