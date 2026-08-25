from __future__ import annotations

from backend.application.runtime.runtime_context import (
    RuntimeContext,
)
from backend.application.runtime.sequential_runtime import (
    SequentialRuntime,
)
from backend.domain.learning.learning_state import (
    LearningState,
)
from backend.domain.workflow.workflow import (
    Workflow,
)


def test_runtime_result_contains_learning_state():

    learning_state = LearningState(
        learner_id="learner-1",
        progress={
            "python": 0.4,
        },
    )

    learning_state.update_mastery(
        "python",
        0.3,
    )

    workflow = Workflow()

    context = RuntimeContext(
        workflow=workflow,
        learning_state=learning_state,
    )

    runtime = SequentialRuntime()

    result = runtime.build_result(
        context,
    )

    assert (
        result.learning_state
        is learning_state
    )


def test_runtime_result_preserves_learning_state_data():

    learning_state = LearningState(
        learner_id="learner-1",
        progress={
            "python": 0.75,
        },
        metadata={
            "level": "beginner",
        },
    )

    learning_state.update_mastery(
        "python",
        0.75,
    )

    workflow = Workflow()

    context = RuntimeContext(
        workflow=workflow,
        learning_state=learning_state,
    )

    runtime = SequentialRuntime()

    result = runtime.build_result(
        context,
    )

    assert (
        result.learning_state is not None
    )

    assert (
        result.learning_state.learner_id
        == "learner-1"
    )

    assert (
        result.learning_state
        .get_knowledge_state("python")
        .mastery
        == 0.75
    )

    assert (
        result.learning_state.get_progress(
            "python",
        )
        == 0.75
    )

    assert (
        result.learning_state.get_metadata(
            "level",
        )
        == "beginner"
    )


def test_runtime_result_contains_default_learning_state():

    workflow = Workflow()

    context = RuntimeContext(
        workflow=workflow,
    )

    runtime = SequentialRuntime()

    result = runtime.build_result(
        context,
    )

    assert (
        result.learning_state
        is not None
    )

    assert (
        result.learning_state.learner_id
        == "default"
    )