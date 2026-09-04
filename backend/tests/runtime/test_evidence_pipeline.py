from __future__ import annotations

from datetime import UTC, datetime, timedelta

from backend.application.runtime.evidence_selector import EvidenceSelector
from backend.application.runtime.runtime_context import RuntimeContext
from backend.core.component_context import ComponentContext
from backend.domain.learning.historical_evidence_builder import (
    HistoricalEvidenceBuilder,
)
from backend.domain.learning.learning_interaction import (
    LearningInteraction,
)
from backend.domain.learning.learning_state import LearningState
from backend.domain.workflow.workflow import Workflow
from backend.domain.workflow.workflow_node import WorkflowNode


# ============================================================
# Helpers
# ============================================================


def make_interaction(
    *,
    learner_id: str = "student-1",
    question_id: str | None = None,
    question: str = "",
    answer: str = "",
    correct: bool | None = None,
    concept_ids: list[str] | None = None,
    timestamp: datetime | None = None,
) -> LearningInteraction:

    return LearningInteraction(
        learner_id=learner_id,
        question_id=question_id,
        question=question,
        answer=answer,
        correct=correct,
        concept_ids=concept_ids or [],
        timestamp=timestamp
        or datetime.now(UTC),
    )


def make_learning_state(
    interactions: list[LearningInteraction],
) -> LearningState:

    return LearningState(
        learner_id="student-1",
        interactions=interactions,
    )


def make_runtime_context(
    learning_state: LearningState,
    *,
    metadata: dict | None = None,
) -> RuntimeContext:

    workflow = Workflow(
        nodes=[],
    )

    return RuntimeContext(
        workflow=workflow,
        learning_state=learning_state,
        metadata=metadata or {},
    )


def make_component_context(
    runtime: RuntimeContext,
) -> ComponentContext:

    node = WorkflowNode(
        id="mentor-1",
        component_id="mentor",
        objective="Teach the learner",
        expected_output="lesson",
    )

    return ComponentContext(
        runtime=runtime,
        node=node,
    )


# ============================================================
# 1. HistoricalEvidenceBuilder
# ============================================================


def test_historical_evidence_builder_selects_recent_interactions():
    now = datetime.now(UTC)

    interactions = [
        make_interaction(
            question_id=str(index),
            question=f"Question {index}",
            timestamp=now + timedelta(minutes=index),
        )
        for index in range(7)
    ]

    learning_state = make_learning_state(
        interactions,
    )

    builder = HistoricalEvidenceBuilder(
        recent_limit=3,
    )

    evidence = builder.build(
        learning_state=learning_state,
        current_question="current question",
    )

    assert len(evidence.recent_interactions) == 3

    assert [
        item.question_id
        for item in evidence.recent_interactions
    ] == ["4", "5", "6"]

    assert evidence.current_question == "current question"

    assert evidence.get_metadata(
        "selection_strategy",
    ) == "recent_and_related_concepts"

    assert evidence.get_metadata(
        "source_interaction_count",
    ) == 7


def test_historical_evidence_builder_selects_related_concepts():
    now = datetime.now(UTC)

    unrelated = make_interaction(
        question_id="1",
        question="Fractions",
        concept_ids=["fraction"],
        timestamp=now,
    )

    related = make_interaction(
        question_id="2",
        question="Triangle angle",
        concept_ids=["triangle", "angle"],
        timestamp=now + timedelta(minutes=1),
    )

    learning_state = make_learning_state(
        [
            unrelated,
            related,
        ],
    )

    builder = HistoricalEvidenceBuilder(
        recent_limit=1,
    )

    evidence = builder.build(
        learning_state=learning_state,
        current_question="triangle question",
        related_concept_ids=["triangle"],
    )

    assert len(evidence.relevant_interactions) == 1

    assert (
        evidence.relevant_interactions[0].question_id
        == "2"
    )

    assert "triangle" in evidence.related_concept_ids
    assert "angle" in evidence.related_concept_ids


# ============================================================
# 2. EvidenceSelector
# ============================================================


def test_evidence_selector_prioritizes_exact_question_id():
    records = [
        {
            "question_id": "100",
            "question": "A different question",
            "concept": "triangle",
            "result": "correct",
        },
        {
            "question_id": "200",
            "question": "The exact historical question",
            "concept": "triangle",
            "result": "wrong",
        },
    ]

    result = EvidenceSelector.select(
        current_question="学生在题目[200]回答的具体内容是什么？",
        current_concept_ids=["triangle"],
        interactions=records,
        top_k=1,
    )

    assert result["stats"]["selected_count"] == 1

    selected = result["history"][0]

    assert selected["question_id"] == "200"


def test_evidence_selector_prioritizes_concept_match():
    records = [
        {
            "question_id": "1",
            "question": "fraction calculation",
            "concept": "fraction",
            "result": "correct",
        },
        {
            "question_id": "2",
            "question": "triangle angle calculation",
            "concept": "triangle",
            "result": "correct",
        },
    ]

    result = EvidenceSelector.select(
        current_question="triangle angle problem",
        current_concept_ids=["triangle"],
        interactions=records,
        top_k=1,
    )

    assert result["stats"]["selected_count"] == 1
    assert result["history"][0]["question_id"] == "2"


def test_evidence_selector_supports_date_match():
    records = [
        {
            "question_id": "1",
            "question": "Old problem",
            "timestamp": "2021-05-28 10:00:00",
        },
        {
            "question_id": "2",
            "question": "Target problem",
            "timestamp": "2021-05-29 10:00:00",
        },
    ]

    result = EvidenceSelector.select(
        current_question=(
            "学生在2021-05-29这一天回答过哪些题目？"
        ),
        current_concept_ids=[],
        interactions=records,
        top_k=1,
    )

    assert result["stats"]["selected_count"] == 1
    assert result["history"][0]["question_id"] == "2"


def test_evidence_selector_prefers_learning_error_signal():
    records = [
        {
            "question_id": "1",
            "question": "triangle angle",
            "concept": "triangle",
            "result": "correct",
        },
        {
            "question_id": "2",
            "question": "triangle angle",
            "concept": "triangle",
            "result": "wrong",
        },
    ]

    result = EvidenceSelector.select(
        current_question="triangle angle",
        current_concept_ids=["triangle"],
        interactions=records,
        top_k=1,
    )

    assert result["stats"]["selected_count"] == 1
    assert result["history"][0]["question_id"] == "2"


def test_evidence_selector_deduplicates_records():
    duplicate = {
        "question_id": "100",
        "question": "triangle question",
        "concept": "triangle",
    }

    result = EvidenceSelector.select(
        current_question="triangle question",
        current_concept_ids=["triangle"],
        interactions=[
            duplicate,
            dict(duplicate),
        ],
        top_k=5,
    )

    assert result["stats"]["selected_count"] == 1
    assert len(result["history"]) == 1


def test_evidence_selector_respects_top_k():
    records = [
        {
            "question_id": str(index),
            "question": "triangle question",
            "concept": "triangle",
        }
        for index in range(10)
    ]

    result = EvidenceSelector.select(
        current_question="triangle question",
        current_concept_ids=["triangle"],
        interactions=records,
        top_k=3,
    )

    assert result["stats"]["selected_count"] == 3
    assert len(result["history"]) == 3


def test_evidence_selector_respects_token_budget():
    records = [
        {
            "question_id": str(index),
            "question": "triangle " * 300,
            "answer": "answer " * 300,
            "concept": "triangle",
        }
        for index in range(5)
    ]

    result = EvidenceSelector.select(
        current_question="triangle question",
        current_concept_ids=["triangle"],
        interactions=records,
        top_k=5,
        max_tokens=100,
    )

    assert (
        result["stats"]["estimated_tokens_after"]
        <= 100
    )


def test_evidence_selector_supports_serialized_json_records():
    record = (
        '{"question_id": "3215", '
        '"question": "triangle problem", '
        '"concept": "triangle", '
        '"result": "wrong"}'
    )

    result = EvidenceSelector.select(
        current_question="题目[3215]的具体内容是什么？",
        current_concept_ids=["triangle"],
        interactions=[record],
        top_k=1,
    )

    assert result["stats"]["selected_count"] == 1
    assert result["history"][0]["question_id"] == "3215"


def test_evidence_selector_supports_related_history():
    result = EvidenceSelector.select(
        current_question="triangle angle problem",
        current_concept_ids=["triangle"],
        interactions=[],
        related_history=[
            {
                "question_id": "999",
                "question": "triangle angle",
                "concept": "triangle",
                "result": "wrong",
            }
        ],
        top_k=1,
    )

    assert result["stats"]["selected_count"] == 1
    assert len(result["related_history"]) == 1
    assert (
        result["related_history"][0]["question_id"]
        == "999"
    )


# ============================================================
# 3. RuntimeContext metadata propagation
# ============================================================


def test_runtime_context_preserves_history_metadata():
    learning_state = make_learning_state([])

    history_info = [
        {
            "question_id": "3215",
            "question": "triangle problem",
            "concept": "triangle",
            "result": "wrong",
        }
    ]

    related_history = [
        {
            "question_id": "999",
            "question": "related triangle problem",
            "concept": "triangle",
        }
    ]

    runtime = make_runtime_context(
        learning_state,
        metadata={
            "current_question": "题目[3215]的具体内容是什么？",
            "current_concept_ids": ["triangle"],
            "history_info": history_info,
            "related_history": related_history,
            "longtutor_features": {
                "accuracy": 0.5,
            },
        },
    )

    assert runtime.get_metadata(
        "current_question",
    ) == "题目[3215]的具体内容是什么？"

    assert runtime.get_metadata(
        "current_concept_ids",
    ) == ["triangle"]

    assert runtime.get_metadata(
        "history_info",
    ) == history_info

    assert runtime.get_metadata(
        "related_history",
    ) == related_history

    assert runtime.get_metadata(
        "longtutor_features",
    ) == {
        "accuracy": 0.5,
    }


# ============================================================
# 4. ContextBuilder integration
# ============================================================


def test_context_builder_selects_runtime_history():
    from backend.infrastructure.prompts.context_builder import (
        ContextBuilder,
    )

    learning_state = make_learning_state([])

    runtime = make_runtime_context(
        learning_state,
        metadata={
            "current_question": (
                "学生在题目[3215]回答的具体内容是什么？"
            ),
            "current_concept_ids": ["triangle"],
            "history_info": [
                {
                    "question_id": "3215",
                    "question": "triangle problem",
                    "answer": "x = 30",
                    "concept": "triangle",
                    "result": "wrong",
                },
                {
                    "question_id": "100",
                    "question": "fraction problem",
                    "answer": "1/2",
                    "concept": "fraction",
                    "result": "correct",
                },
            ],
        },
    )

    context = make_component_context(
        runtime,
    )

    builder = ContextBuilder()

    messages = builder.build(
        context=context,
        system_prompt="You are a tutor.",
    )

    combined = "\n".join(
        message["content"]
        for message in messages
    )

    assert "RELEVANT LEARNING HISTORY" in combined

    assert "3215" in combined

    assert "triangle problem" in combined


def test_context_builder_uses_related_history():
    from backend.infrastructure.prompts.context_builder import (
        ContextBuilder,
    )

    learning_state = make_learning_state([])

    runtime = make_runtime_context(
        learning_state,
        metadata={
            "current_question": "triangle angle problem",
            "current_concept_ids": ["triangle"],
            "related_history": [
                {
                    "question_id": "500",
                    "question": "related triangle problem",
                    "answer": "60",
                    "concept": "triangle",
                    "result": "wrong",
                }
            ],
        },
    )

    context = make_component_context(
        runtime,
    )

    builder = ContextBuilder()

    messages = builder.build(
        context=context,
        system_prompt="You are a tutor.",
    )

    combined = "\n".join(
        message["content"]
        for message in messages
    )

    assert "RELEVANT RELATED-CONCEPT HISTORY" in combined

    assert "500" in combined

    assert "related triangle problem" in combined


# ============================================================
# 5. Gold isolation
# ============================================================


def test_context_builder_does_not_use_gold_memory_queries():
    from backend.infrastructure.prompts.context_builder import (
        ContextBuilder,
    )

    learning_state = make_learning_state([])

    runtime = make_runtime_context(
        learning_state,
        metadata={
            "current_question": "triangle question",
            "current_concept_ids": ["triangle"],
            "gold_memory_queries": [
                "This must never reach the context."
            ],
            "history_info": [
                {
                    "question_id": "1",
                    "question": "triangle question",
                    "concept": "triangle",
                    "result": "wrong",
                }
            ],
        },
    )

    context = make_component_context(
        runtime,
    )

    builder = ContextBuilder()

    messages = builder.build(
        context=context,
        system_prompt="You are a tutor.",
    )

    combined = "\n".join(
        message["content"]
        for message in messages
    )

    assert (
        "This must never reach the context."
        not in combined
    )

    assert "triangle question" in combined


# ============================================================
# 6. Full pipeline
# ============================================================


def test_evidence_pipeline_builder_selector_context():
    now = datetime.now(UTC)

    interactions = [
        make_interaction(
            question_id="1",
            question="fraction calculation",
            answer="1/2",
            correct=True,
            concept_ids=["fraction"],
            timestamp=now,
        ),
        make_interaction(
            question_id="3215",
            question="triangle angle problem",
            answer="wrong answer",
            correct=False,
            concept_ids=["triangle", "angle"],
            timestamp=now + timedelta(minutes=1),
        ),
    ]

    learning_state = make_learning_state(
        interactions,
    )

    # ----------------------------------------------
    # Domain evidence construction
    # ----------------------------------------------

    evidence_builder = HistoricalEvidenceBuilder(
        recent_limit=5,
    )

    evidence = evidence_builder.build(
        learning_state=learning_state,
        current_question=(
            "学生在题目[3215]回答的具体内容是什么？"
        ),
        related_concept_ids=["triangle"],
    )

    assert evidence.has_evidence

    assert any(
        item.question_id == "3215"
        for item in evidence.relevant_interactions
    )

    # ----------------------------------------------
    # Runtime selection
    # ----------------------------------------------

    selection = EvidenceSelector.select(
        current_question=(
            "学生在题目[3215]回答的具体内容是什么？"
        ),
        current_concept_ids=["triangle"],
        interactions=(
            evidence.relevant_interactions
            + evidence.recent_interactions
        ),
        top_k=5,
    )

    assert selection["stats"]["selected_count"] >= 1

    assert any(
        item["question_id"] == "3215"
        for item in selection["history"]
    )

    # ----------------------------------------------
    # Context construction
    # ----------------------------------------------

    runtime = make_runtime_context(
        learning_state,
        metadata={
            "current_question": (
                "学生在题目[3215]回答的具体内容是什么？"
            ),
            "current_concept_ids": ["triangle"],
        },
    )

    component_context = make_component_context(
        runtime,
    )

    from backend.infrastructure.prompts.context_builder import (
        ContextBuilder,
    )

    context_builder = ContextBuilder(
        evidence_builder=evidence_builder,
    )

    messages = context_builder.build(
        context=component_context,
        system_prompt="You are a tutor.",
    )

    combined = "\n".join(
        message["content"]
        for message in messages
    )

    assert "CURRENT QUESTION" in combined
    assert "RELEVANT LEARNING HISTORY" in combined
    assert "3215" in combined
    assert "triangle angle problem" in combined