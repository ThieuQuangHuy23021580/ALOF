from __future__ import annotations

from backend.domain.knowledge.knowledge_level import (
    KnowledgeLevel,
)
from backend.domain.learning.adaptive_teaching_action import (
    AdaptiveTeachingActionSelector,
    TeachingActionType,
    TeachingStrategy,
)
from backend.domain.learning.knowledge_diagnosis import (
    ConceptDiagnosis,
    KnowledgeDiagnosis,
)


def make_diagnosis(
    concepts: list[ConceptDiagnosis],
    weak_concepts: list[str] | None = None,
    transfer_deficit_concepts: list[str] | None = None,
) -> KnowledgeDiagnosis:

    return KnowledgeDiagnosis(
        learner_id="learner-1",
        current_question="Current question",
        concepts={
            concept.concept_id: concept
            for concept in concepts
        },
        primary_concepts=[
            concept.concept_id
            for concept in concepts
        ],
        weak_concepts=(
            weak_concepts
            or []
        ),
        transfer_deficit_concepts=(
            transfer_deficit_concepts
            or []
        ),
    )


def make_concept(
    concept_id: str,
    mastery: float,
) -> ConceptDiagnosis:

    if mastery <= 0.0:
        level = KnowledgeLevel.UNKNOWN
    elif mastery < 0.4:
        level = KnowledgeLevel.BEGINNER
    elif mastery < 0.7:
        level = KnowledgeLevel.INTERMEDIATE
    elif mastery < 0.9:
        level = KnowledgeLevel.ADVANCED
    else:
        level = KnowledgeLevel.MASTERED

    return ConceptDiagnosis(
        concept_id=concept_id,
        mastery=mastery,
        level=level,
    )


def test_selects_introduce_when_no_diagnosis():

    diagnosis = KnowledgeDiagnosis(
        learner_id="learner-1",
        current_question="Explain Python.",
    )

    action = AdaptiveTeachingActionSelector().select(
        diagnosis,
    )

    assert (
        action.action
        == TeachingActionType.INTRODUCE
    )

    assert (
        action.strategy
        == TeachingStrategy.DIRECT_EXPLANATION
    )

    assert action.difficulty == "beginner"


def test_selects_scaffold_for_transfer_deficit():

    diagnosis = make_diagnosis(
        concepts=[
            make_concept(
                "recursion",
                0.5,
            ),
        ],
        transfer_deficit_concepts=[
            "recursion",
        ],
    )

    action = AdaptiveTeachingActionSelector().select(
        diagnosis,
    )

    assert (
        action.action
        == TeachingActionType.SCAFFOLD
    )

    assert (
        action.strategy
        == TeachingStrategy.STEP_BY_STEP
    )

    assert action.difficulty == "medium"

    assert action.focus_concepts == [
        "recursion",
    ]

    assert (
        action.metadata["decision_signal"]
        == "transfer_deficit"
    )


def test_selects_explanation_for_weak_knowledge():

    diagnosis = make_diagnosis(
        concepts=[
            make_concept(
                "python",
                0.2,
            ),
        ],
        weak_concepts=[
            "python",
        ],
    )

    action = AdaptiveTeachingActionSelector().select(
        diagnosis,
    )

    assert (
        action.action
        == TeachingActionType.EXPLAIN
    )

    assert (
        action.strategy
        == TeachingStrategy.GUIDED_EXPLANATION
    )

    assert action.difficulty == "beginner"

    assert action.focus_concepts == [
        "python",
    ]


def test_selects_practice_for_partial_mastery():

    diagnosis = make_diagnosis(
        concepts=[
            make_concept(
                "python",
                0.5,
            ),
        ],
    )

    action = AdaptiveTeachingActionSelector().select(
        diagnosis,
    )

    assert (
        action.action
        == TeachingActionType.PRACTICE
    )

    assert (
        action.strategy
        == TeachingStrategy.TARGETED_PRACTICE
    )

    assert action.difficulty == "medium"

    assert action.focus_concepts == [
        "python",
    ]


def test_selects_challenge_for_strong_mastery():

    diagnosis = make_diagnosis(
        concepts=[
            make_concept(
                "python",
                0.8,
            ),
        ],
    )

    action = AdaptiveTeachingActionSelector().select(
        diagnosis,
    )

    assert (
        action.action
        == TeachingActionType.CHALLENGE
    )

    assert (
        action.strategy
        == TeachingStrategy.DEEPENING
    )

    assert action.difficulty == "advanced"

    assert action.focus_concepts == [
        "python",
    ]


def test_transfer_deficit_has_priority_over_weakness():

    diagnosis = make_diagnosis(
        concepts=[
            make_concept(
                "python",
                0.2,
            ),
        ],
        weak_concepts=[
            "python",
        ],
        transfer_deficit_concepts=[
            "python",
        ],
    )

    action = AdaptiveTeachingActionSelector().select(
        diagnosis,
    )

    assert (
        action.action
        == TeachingActionType.SCAFFOLD
    )

    assert (
        action.metadata["decision_signal"]
        == "transfer_deficit"
    )


def test_action_focus_can_be_extended():

    diagnosis = make_diagnosis(
        concepts=[
            make_concept(
                "python",
                0.2,
            ),
        ],
        weak_concepts=[
            "python",
        ],
    )

    action = AdaptiveTeachingActionSelector().select(
        diagnosis,
    )

    action.add_focus_concept(
        "functions",
    )

    action.add_focus_concept(
        "python",
    )

    assert action.focus_concepts == [
        "python",
        "functions",
    ]