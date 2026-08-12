from __future__ import annotations

from backend.application.runtime.runtime_context import (
    RuntimeContext,
)
from backend.domain.learning.learning_state import (
    LearningState,
)
from backend.domain.workflow.workflow import (
    Workflow,
)


def test_runtime_context_creates_default_learning_state():

    workflow = Workflow()

    context = RuntimeContext(
        workflow=workflow,
    )

    assert isinstance(
        context.learning_state,
        LearningState,
    )

    assert (
        context.learning_state.learner_id
        == "default"
    )


def test_runtime_context_accepts_custom_learning_state():

    workflow = Workflow()

    learning_state = LearningState(
        learner_id="learner-1",
        current_knowledge={
            "python": "basic",
        },
        progress={
            "python": 0.5,
        },
    )

    context = RuntimeContext(
        workflow=workflow,
        learning_state=learning_state,
    )

    assert (
        context.learning_state
        is learning_state
    )

    assert (
        context.learning_state.learner_id
        == "learner-1"
    )

    assert (
        context.learning_state.get_knowledge(
            "python",
        )
        == "basic"
    )

    assert (
        context.learning_state.get_progress(
            "python",
        )
        == 0.5
    )


def test_runtime_context_learning_state_can_be_updated():

    workflow = Workflow()

    context = RuntimeContext(
        workflow=workflow,
    )

    context.learning_state.update_knowledge(
        "python",
        "intermediate",
    )

    context.learning_state.update_progress(
        "python",
        0.75,
    )

    assert (
        context.learning_state.get_knowledge(
            "python",
        )
        == "intermediate"
    )

    assert (
        context.learning_state.get_progress(
            "python",
        )
        == 0.75
    )


def test_runtime_context_learning_states_are_isolated():

    workflow = Workflow()

    first = RuntimeContext(
        workflow=workflow,
    )

    second = RuntimeContext(
        workflow=workflow,
    )

    first.learning_state.update_knowledge(
        "python",
        "basic",
    )

    first.learning_state.update_progress(
        "python",
        0.5,
    )

    assert (
        second.learning_state.current_knowledge
        == {}
    )

    assert (
        second.learning_state.progress
        == {}
    )