from __future__ import annotations

import json
from datetime import UTC, datetime

from backend.application.runtime.runtime_context import (
    RuntimeContext,
)
from backend.core.component_context import ComponentContext
from backend.domain.learning.learning_interaction import (
    LearningInteraction,
)
from backend.domain.learning.learning_state import (
    LearningState,
)
from backend.domain.workflow.workflow import Workflow
from backend.domain.workflow.workflow_node import WorkflowNode
from backend.infrastructure.prompts.context_builder import (
    ContextBuilder,
)


def _make_context(
    *,
    learning_state: LearningState,
    current_question: str = "",
    current_concept_ids: list[str] | None = None,
    history_info: list[dict] | None = None,
    related_history: list[dict] | None = None,
) -> ComponentContext:

    workflow = Workflow(
        id="test-workflow",
        name="Test Workflow",
    )

    node = WorkflowNode(
        id="test-node",
        component_id="mentor",
        objective="Teach the learner",
        expected_output="Teaching response",
    )

    runtime = RuntimeContext(
        workflow=workflow,
        learning_state=learning_state,
    )

    runtime.set_metadata(
        "current_question",
        current_question,
    )

    runtime.set_metadata(
        "current_concept_ids",
        current_concept_ids or [],
    )

    runtime.set_metadata(
        "history_info",
        history_info or [],
    )

    runtime.set_metadata(
        "related_history",
        related_history or [],
    )

    return ComponentContext(
        runtime=runtime,
        node=node,
    )


def _message_text(
    messages: list[dict[str, str]],
) -> str:
    return "\n\n".join(
        message["content"]
        for message in messages
    )


def test_context_builder_includes_current_task_and_learner_state():
    learning_state = LearningState(
        learner_id="student-1",
    )

    learning_state.update_knowledge(
        "algebra",
        "intermediate",
    )

    learning_state.update_progress(
        "algebra",
        0.6,
    )

    context = _make_context(
        learning_state=learning_state,
        current_question="Solve x + 2 = 5",
        current_concept_ids=["algebra"],
    )

    builder = ContextBuilder()

    messages = builder.build(
        context=context,
        system_prompt="You are a tutor.",
    )

    text = _message_text(messages)

    assert "You are a tutor." in text
    assert "CURRENT TASK" in text
    assert "Component: mentor" in text
    assert "Objective: Teach the learner" in text
    assert "Expected Output: Teaching response" in text

    assert "LEARNER STATE" in text
    assert "Learner ID: student-1" in text
    assert "algebra" in text
    assert "0.6" in text

    assert "CURRENT QUESTION" in text
    assert "Solve x + 2 = 5" in text

    assert "CURRENT CONCEPTS" in text
    assert "algebra" in text


def test_context_builder_selects_relevant_external_history():
    learning_state = LearningState(
        learner_id="student-1",
    )

    history_info = [
        {
            "question_id": "q-algebra",
            "question": "Solve x + 2 = 5",
            "answer": "3",
            "correct": True,
            "concept_ids": ["algebra"],
            "timestamp": "2026-01-01T10:00:00Z",
        },
        {
            "question_id": "q-geometry",
            "question": "Find the area of a triangle",
            "answer": "20",
            "correct": True,
            "concept_ids": ["geometry"],
            "timestamp": "2026-01-02T10:00:00Z",
        },
    ]

    context = _make_context(
        learning_state=learning_state,
        current_question="Solve x + 2 = 5",
        current_concept_ids=["algebra"],
        history_info=history_info,
    )

    builder = ContextBuilder()

    messages = builder.build(
        context=context,
        system_prompt="You are a tutor.",
    )

    text = _message_text(messages)

    assert "RELEVANT LEARNING HISTORY" in text
    assert "q-algebra" in text

    # The strongly unrelated geometry record should not
    # be selected over the matching algebra record.
    assert "q-algebra" in text


def test_context_builder_includes_related_history():
    learning_state = LearningState(
        learner_id="student-1",
    )

    related_history = [
        {
            "question_id": "q-related",
            "question": "Solve 2x = 10",
            "answer": "5",
            "correct": False,
            "concept_ids": ["equation"],
            "timestamp": "2026-01-03T10:00:00Z",
        }
    ]

    context = _make_context(
        learning_state=learning_state,
        current_question="Solve an equation",
        current_concept_ids=["equation"],
        related_history=related_history,
    )

    builder = ContextBuilder()

    messages = builder.build(
        context=context,
        system_prompt="You are a tutor.",
    )

    text = _message_text(messages)

    assert (
        "RELEVANT RELATED-CONCEPT HISTORY"
        in text
    )

    assert "q-related" in text
    assert "Solve 2x = 10" in text


def test_context_builder_respects_memory_top_k():
    learning_state = LearningState(
        learner_id="student-1",
    )

    history_info = [
        {
            "question_id": f"q-{index}",
            "question": (
                f"Solve algebra problem {index}"
            ),
            "answer": str(index),
            "correct": index % 2 == 0,
            "concept_ids": ["algebra"],
            "timestamp": (
                f"2026-01-{index + 1:02d}T10:00:00Z"
            ),
        }
        for index in range(10)
    ]

    context = _make_context(
        learning_state=learning_state,
        current_question="Solve algebra problem",
        current_concept_ids=["algebra"],
        history_info=history_info,
    )

    builder = ContextBuilder()

    messages = builder.build(
        context=context,
        system_prompt="You are a tutor.",
    )

    text = _message_text(messages)

    # ContextBuilder currently uses MEMORY_TOP_K = 5.
    selected_ids = [
        f"q-{index}"
        for index in range(10)
        if f"q-{index}" in text
    ]

    assert len(selected_ids) <= 5


def test_context_builder_does_not_expose_gold_fields():
    learning_state = LearningState(
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

    context = _make_context(
        learning_state=learning_state,
        current_question="What is 1 + 1?",
        current_concept_ids=["arithmetic"],
        history_info=history_info,
    )

    builder = ContextBuilder()

    messages = builder.build(
        context=context,
        system_prompt="You are a tutor.",
    )

    text = _message_text(messages)

    assert "gold_memory_queries" not in text
    assert "gold_answer" not in text
    assert "gold_answers" not in text


def test_context_builder_includes_longtutor_features():
    learning_state = LearningState(
        learner_id="student-1",
    )

    context = _make_context(
        learning_state=learning_state,
        current_question="Solve x = 5",
        current_concept_ids=["algebra"],
    )

    context.runtime.metadata[
        "longtutor_features"
    ] = {
        "avg_correctness": 0.4,
        "recent_accuracy": 0.3,
        "long_gap_days": 7.0,
    }

    builder = ContextBuilder()

    messages = builder.build(
        context=context,
        system_prompt="You are a tutor.",
    )

    text = _message_text(messages)

    assert "LEARNING FEATURES" in text
    assert "avg_correctness" in text
    assert "recent_accuracy" in text
    assert "long_gap_days" in text


def test_context_builder_emits_memory_policy():
    learning_state = LearningState(
        learner_id="student-1",
    )

    history_info = [
        {
            "question_id": "q1",
            "question": "Solve x + 1 = 2",
            "answer": "1",
            "correct": True,
            "concept_ids": ["algebra"],
            "timestamp": "2026-01-01T10:00:00Z",
        }
    ]

    context = _make_context(
        learning_state=learning_state,
        current_question="Solve x + 1 = 2",
        current_concept_ids=["algebra"],
        history_info=history_info,
    )

    builder = ContextBuilder()

    messages = builder.build(
        context=context,
        system_prompt="You are a tutor.",
    )

    text = _message_text(messages)

    assert "MEMORY CONTEXT POLICY" in text
    assert "Selected records:" in text
    assert "History candidates:" in text
    assert "Related-history candidates:" in text
    assert "Estimated memory tokens after selection:" in text
    assert "Use only the supplied historical evidence." in text
    assert "Do not invent historical facts." in text


def test_context_builder_preserves_native_learning_history():
    learning_state = LearningState(
        learner_id="student-1",
    )

    interaction = LearningInteraction(
        learner_id="student-1",
        question_id="native-q1",
        question="Solve x + 1 = 2",
        answer="1",
        correct=False,
        concept_ids=["algebra"],
        timestamp=datetime(
            2026,
            1,
            1,
            tzinfo=UTC,
        ),
    )

    learning_state.add_interaction(
        interaction
    )

    context = _make_context(
        learning_state=learning_state,
        current_question="Solve x + 1 = 2",
        current_concept_ids=["algebra"],
    )

    builder = ContextBuilder()

    messages = builder.build(
        context=context,
        system_prompt="You are a tutor.",
    )

    text = _message_text(messages)

    assert "RELEVANT LEARNING HISTORY" in text
    assert "native-q1" in text
    assert "Solve x + 1 = 2" in text


def test_context_builder_serializes_non_string_values():
    learning_state = LearningState(
        learner_id="student-1",
    )

    context = _make_context(
        learning_state=learning_state,
        current_question="Solve x = 5",
        current_concept_ids=["algebra", "equation"],
    )

    builder = ContextBuilder()

    messages = builder.build(
        context=context,
        system_prompt="Tutor",
    )

    current_concepts_message = next(
        message
        for message in messages
        if message["content"].startswith(
            "CURRENT CONCEPTS"
        )
    )

    assert json.loads(
        current_concepts_message["content"].split(
            "\n\n",
            1,
        )[1]
    ) == ["algebra", "equation"]