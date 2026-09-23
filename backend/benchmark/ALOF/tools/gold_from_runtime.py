from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from backend.application.orchestration.adaptive_learning_pipeline import (
    AdaptiveLearningPipeline,
)
from backend.application.runtime.evidence_selector import EvidenceSelector
from backend.domain.learning.historical_evidence_builder import (
    HistoricalEvidenceBuilder,
)
from backend.domain.learning.learning_interaction import LearningInteraction
from backend.domain.learning.learning_state import LearningState
from backend.infrastructure.prompts.context_builder import ContextBuilder


def parse_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        timestamp = value
    elif isinstance(value, (int, float)):
        timestamp = datetime.fromtimestamp(value, tz=UTC)
    else:
        text = str(value or "").strip()
        if not text:
            return datetime.fromtimestamp(0, tz=UTC)
        try:
            timestamp = datetime.fromisoformat(
                text.replace("Z", "+00:00")
            )
        except ValueError:
            return datetime.fromtimestamp(0, tz=UTC)

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=UTC)
    return timestamp.astimezone(UTC)


def build_learning_state(sample: dict[str, Any]) -> LearningState:
    learner = sample.get("learner") or {}
    learner_id = str(
        learner.get("id")
        or learner.get("learner_id")
        or sample["case_id"]
    )
    state = LearningState(learner_id=learner_id)

    for raw in sample.get("history") or []:
        if not isinstance(raw, dict):
            continue

        interaction_data: dict[str, Any] = {
            "learner_id": learner_id,
            "question_id": raw.get("question_id"),
            "question": str(raw.get("question", "")),
            "answer": str(raw.get("answer", "")),
            "correct": raw.get("correct"),
            "concept_ids": list(raw.get("concept_ids", [])),
        }
        timestamp = raw.get("timestamp")
        if timestamp is not None:
            interaction_data["timestamp"] = parse_timestamp(timestamp)

        metadata = raw.get("metadata")
        if isinstance(metadata, dict):
            interaction_data["metadata"] = metadata

        state.add_interaction(LearningInteraction(**interaction_data))

    return state


def _task_fields(sample: dict[str, Any]) -> tuple[str, list[str]]:
    task = sample["current_task"]
    question = str(task.get("question") or task.get("content") or "")
    concept_ids = [str(v) for v in (task.get("concept_ids") or [])]
    return question, concept_ids


def select_memory(sample: dict[str, Any]) -> dict[str, Any]:
    question, concept_ids = _task_fields(sample)
    state = build_learning_state(sample)
    evidence = HistoricalEvidenceBuilder(recent_limit=5).build(
        learning_state=state,
        current_question=question,
        related_concept_ids=concept_ids,
    )

    relevant_ids = sorted(
        {
            str(interaction.question_id).strip()
            for interaction in evidence.relevant_interactions
            if interaction.question_id
        }
    )

    seen_ids: set[str] = set()
    interactions: list[LearningInteraction] = []
    for interaction in (
        list(evidence.relevant_interactions)
        + list(evidence.recent_interactions)
    ):
        if interaction.id in seen_ids:
            continue
        seen_ids.add(interaction.id)
        interactions.append(interaction)

    selection = EvidenceSelector.select(
        current_question=question,
        current_concept_ids=concept_ids,
        interactions=interactions,
        related_history=list(evidence.related_interactions),
        top_k=ContextBuilder.MEMORY_TOP_K,
        max_tokens=ContextBuilder.MEMORY_MAX_TOKENS,
    )
    selection["relevant_interactions"] = relevant_ids
    return selection


def compute_memory_gold(sample: dict[str, Any]) -> dict[str, list[str]]:
    selection = select_memory(sample)
    top_k_ids: list[str] = []
    for record in selection["history"] + selection["related_history"]:
        qid = str(record.get("question_id") or "").strip()
        if not qid:
            raise ValueError(
                f"{sample.get('case_id')}: memory record missing question_id"
            )
        top_k_ids.append(qid)

    return {
        "relevant_interactions": selection["relevant_interactions"],
        "top_k_interactions": top_k_ids,
    }


def compute_diagnosis_strategy_gold(
    sample: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    question, concept_ids = _task_fields(sample)
    state = build_learning_state(sample)
    result = AdaptiveLearningPipeline().run(
        learning_state=state,
        current_question=question,
        related_concept_ids=concept_ids,
        primary_concept_ids=concept_ids,
    )

    diagnosis = result.diagnosis
    primary = (
        diagnosis.primary_concepts[0]
        if diagnosis.primary_concepts
        else None
    )
    primary_state = (
        diagnosis.concepts.get(primary)
        if primary
        else None
    )

    diagnosis_gold: dict[str, Any] = {}
    if primary:
        diagnosis_gold["concept"] = primary
    if primary_state is not None:
        diagnosis_gold["level"] = str(primary_state.level)
    diagnosis_gold["weak_concepts"] = list(diagnosis.weak_concepts)

    action = result.teaching_action
    strategy_gold = {
        "action": str(action.action),
        "strategy": str(action.strategy),
        "difficulty": str(action.difficulty),
        "focus_concepts": list(action.focus_concepts),
    }

    return {
        "diagnosis": diagnosis_gold,
        "strategy": strategy_gold,
    }


def compute_runtime_gold(sample: dict[str, Any]) -> dict[str, Any]:
    memory = compute_memory_gold(sample)
    rest = compute_diagnosis_strategy_gold(sample)
    return {
        "memory": memory,
        **rest,
    }
