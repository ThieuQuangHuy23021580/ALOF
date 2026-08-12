from __future__ import annotations

from backend.domain.learning.learning_state import (
    LearningState,
)


def test_learning_state_defaults():

    state = LearningState(
        learner_id="learner-1",
    )

    assert (
        state.learner_id
        == "learner-1"
    )

    assert (
        state.current_knowledge
        == {}
    )

    assert (
        state.progress
        == {}
    )

    assert (
        state.metadata
        == {}
    )


def test_learning_state_stores_current_knowledge():

    state = LearningState(
        learner_id="learner-1",
        current_knowledge={
            "python": "basic",
            "variables": "understood",
        },
    )

    assert (
        state.current_knowledge["python"]
        == "basic"
    )

    assert (
        state.current_knowledge["variables"]
        == "understood"
    )


def test_learning_state_stores_progress():

    state = LearningState(
        learner_id="learner-1",
        progress={
            "python": 0.5,
            "variables": 1.0,
        },
    )

    assert (
        state.progress["python"]
        == 0.5
    )

    assert (
        state.progress["variables"]
        == 1.0
    )


def test_learning_state_stores_metadata():

    state = LearningState(
        learner_id="learner-1",
        metadata={
            "level": "beginner",
            "source": "initial_assessment",
        },
    )

    assert (
        state.metadata["level"]
        == "beginner"
    )

    assert (
        state.metadata["source"]
        == "initial_assessment"
    )

def test_learning_state_updates_knowledge():

    state = LearningState(
        learner_id="learner-1",
    )

    state.update_knowledge(
        "python",
        "basic",
    )

    assert (
        state.get_knowledge("python")
        == "basic"
    )


def test_learning_state_get_unknown_knowledge():

    state = LearningState(
        learner_id="learner-1",
    )

    assert (
        state.get_knowledge("python")
        is None
    )

    assert (
        state.get_knowledge(
            "python",
            "unknown",
        )
        == "unknown"
    )


def test_learning_state_updates_progress():

    state = LearningState(
        learner_id="learner-1",
    )

    state.update_progress(
        "python",
        0.5,
    )

    assert (
        state.get_progress("python")
        == 0.5
    )


def test_learning_state_get_unknown_progress():

    state = LearningState(
        learner_id="learner-1",
    )

    assert (
        state.get_progress("python")
        is None
    )

    assert (
        state.get_progress(
            "python",
            0.0,
        )
        == 0.0
    )


def test_learning_state_sets_metadata():

    state = LearningState(
        learner_id="learner-1",
    )

    state.set_metadata(
        "level",
        "beginner",
    )

    assert (
        state.get_metadata("level")
        == "beginner"
    )


def test_learning_state_get_unknown_metadata():

    state = LearningState(
        learner_id="learner-1",
    )

    assert (
        state.get_metadata("level")
        is None
    )

    assert (
        state.get_metadata(
            "level",
            "unknown",
        )
        == "unknown"
    )


def test_learning_states_are_isolated():

    first = LearningState(
        learner_id="learner-1",
    )

    second = LearningState(
        learner_id="learner-2",
    )

    first.update_knowledge(
        "python",
        "basic",
    )

    first.update_progress(
        "python",
        0.5,
    )

    first.set_metadata(
        "level",
        "beginner",
    )

    assert (
        second.current_knowledge
        == {}
    )

    assert (
        second.progress
        == {}
    )

    assert (
        second.metadata
        == {}
    )