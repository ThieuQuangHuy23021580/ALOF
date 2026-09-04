from __future__ import annotations

import json
from typing import Any

from backend.application.runtime.evidence_selector import (
    EvidenceSelector,
)
from backend.core.component_context import ComponentContext
from backend.domain.learning.historical_evidence_builder import (
    HistoricalEvidenceBuilder,
)
from backend.domain.learning.learning_interaction import (
    LearningInteraction,
)


class ContextBuilder:
    """
    Build the LLM context for a component.

    Responsibilities
    ----------------
    - Build task and learner-state context.
    - Build historical evidence from LearningState.
    - Preserve relevant and related evidence semantics.
    - Select evidence deterministically.
    - Format selected evidence for the LLM.

    ContextBuilder does NOT:
    - call an LLM;
    - perform diagnosis;
    - access Gold benchmark answers;
    - implement evidence ranking logic.
    """

    MEMORY_TOP_K = 5
    MEMORY_MAX_TOKENS = 1200

    def __init__(
        self,
        evidence_builder: HistoricalEvidenceBuilder | None = None,
    ) -> None:

        self._evidence_builder = (
            evidence_builder
            if evidence_builder is not None
            else HistoricalEvidenceBuilder()
        )

    def build(
        self,
        context: ComponentContext,
        system_prompt: str,
    ) -> list[dict[str, str]]:

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]

        node = context.node
        runtime = context.runtime
        learning_state = runtime.learning_state

        # ==================================================
        # 1. CURRENT TASK
        # ==================================================

        messages.append(
            {
                "role": "system",
                "content": (
                    "CURRENT TASK\n\n"
                    f"Component: {node.component_id}\n"
                    f"Objective: {node.objective}\n"
                    f"Expected Output: {node.expected_output}"
                ),
            }
        )

        # ==================================================
        # 2. ADAPTIVE TEACHING DECISION
        # ==================================================

        if node.has_adaptive_action:

            focus_concepts = json.dumps(
                node.focus_concepts,
                ensure_ascii=False,
            )

            messages.append(
                {
                    "role": "system",
                    "content": (
                        "ADAPTIVE TEACHING DECISION\n\n"
                        f"Action: {node.action}\n"
                        f"Strategy: {node.strategy}\n"
                        f"Difficulty: {node.difficulty}\n"
                        f"Focus Concepts: {focus_concepts}\n\n"
                        "You MUST use this adaptive teaching decision "
                        "when generating the response. "
                        "The selected strategy must be reflected in "
                        "the actual teaching approach, not merely "
                        "mentioned as a label."
                    ),
                }
            )

        # ==================================================
        # 3. LEARNER STATE
        # ==================================================

        messages.append(
            {
                "role": "system",
                "content": (
                    "LEARNER STATE\n\n"
                    f"Learner ID: {learning_state.learner_id}\n"
                    f"Current Knowledge: "
                    f"{learning_state.current_knowledge}\n"
                    f"Progress: {learning_state.progress}"
                ),
            }
        )

        # ==================================================
        # 4. RUNTIME METADATA
        # ==================================================

        metadata = getattr(
            learning_state,
            "metadata",
            {},
        )

        if not isinstance(
            metadata,
            dict,
        ):
            metadata = {}

        runtime_metadata = getattr(
            runtime,
            "metadata",
            {},
        )

        if not isinstance(
            runtime_metadata,
            dict,
        ):
            runtime_metadata = {}

        current_question = runtime_metadata.get(
            "current_question",
            metadata.get(
                "current_question",
            ),
        )

        current_concept_ids = runtime_metadata.get(
            "current_concept_ids",
            metadata.get(
                "current_concept_ids",
                [],
            ),
        )

        if not isinstance(
            current_concept_ids,
            list,
        ):
            current_concept_ids = []

        # ==================================================
        # 5. CURRENT QUESTION
        # ==================================================

        if current_question:

            messages.append(
                {
                    "role": "system",
                    "content": (
                        "CURRENT QUESTION\n\n"
                        f"{self._serialize(current_question)}"
                    ),
                }
            )

        # ==================================================
        # 6. CURRENT CONCEPTS
        # ==================================================

        if current_concept_ids:

            messages.append(
                {
                    "role": "system",
                    "content": (
                        "CURRENT CONCEPTS\n\n"
                        f"{self._serialize(current_concept_ids)}"
                    ),
                }
            )

        # ==================================================
        # 7. LONGTUTOR FEATURES
        # ==================================================

        longtutor_features = runtime_metadata.get(
            "longtutor_features",
            metadata.get(
                "longtutor_features",
                {},
            ),
        )

        if longtutor_features:

            messages.append(
                {
                    "role": "system",
                    "content": (
                        "LEARNING FEATURES\n\n"
                        "Use these learner-specific features "
                        "to adapt teaching when relevant. "
                        "Do not mention internal feature values "
                        "directly to the learner.\n\n"
                        f"{self._serialize(longtutor_features)}"
                    ),
                }
            )

        # ==================================================
        # 8. EXTERNAL HISTORY
        # ==================================================

        external_history = runtime_metadata.get(
            "history_info",
            runtime_metadata.get(
                "history",
                [],
            ),
        )

        if not isinstance(
            external_history,
            list,
        ):
            external_history = []

        external_related_history = runtime_metadata.get(
            "related_history",
            [],
        )

        if not isinstance(
            external_related_history,
            list,
        ):
            external_related_history = []

        # ==================================================
        # 9. HISTORICAL EVIDENCE
        # ==================================================

        historical_evidence = (
            self._evidence_builder.build(
                learning_state=learning_state,
                current_question=str(
                    current_question or "",
                ),
                related_concept_ids=[
                    str(value)
                    for value in current_concept_ids
                ],
                history_info=external_history,
                related_history=external_related_history,
            )
        )

        # ==================================================
        # 10. CANONICAL EVIDENCE CANDIDATES
        # ==================================================

        interactions: list[LearningInteraction] = []

        seen_ids: set[str] = set()

        for interaction in (
            list(historical_evidence.relevant_interactions)
            + list(historical_evidence.recent_interactions)
        ):
            if interaction.id in seen_ids:
                continue

            seen_ids.add(interaction.id)
            interactions.append(interaction)

        related_interactions = list(
            historical_evidence.related_interactions
        )

        memory_selection = EvidenceSelector.select(
            current_question=str(
                current_question or "",
            ),
            current_concept_ids=[
                str(value)
                for value in current_concept_ids
            ],
            interactions=interactions,
            related_history=related_interactions,
            top_k=self.MEMORY_TOP_K,
            max_tokens=self.MEMORY_MAX_TOKENS,
        )

        context.runtime.set_metadata(
            "memory_selection_debug",
            memory_selection["stats"].get("debug", {}),
        )

        context.runtime.set_metadata(
            "memory_retrieval",
            (
                list(memory_selection["history"])
                + list(memory_selection["related_history"])
            ),
        )

        selected_history = memory_selection[
            "history"
        ]

        selected_related_history = memory_selection[
            "related_history"
        ]

        memory_stats = memory_selection[
            "stats"
        ]

        # ==================================================
        # 11. SELECTED HISTORY
        # ==================================================

        if selected_history:

            history_json = json.dumps(
                selected_history,
                ensure_ascii=False,
                default=str,
            )

            messages.append(
                {
                    "role": "system",
                    "content": (
                        "RELEVANT LEARNING HISTORY\n\n"
                        "These are historical learning "
                        "interactions selected as relevant "
                        "to the CURRENT QUESTION.\n\n"
                        "Use them to personalize teaching, "
                        "identify previous mistakes, successful "
                        "attempts, repeated patterns, or "
                        "knowledge gaps.\n\n"
                        "Do not treat unrelated historical "
                        "records as evidence for the CURRENT "
                        "QUESTION.\n\n"
                        f"{history_json}"
                    ),
                }
            )

        # ==================================================
        # 12. SELECTED RELATED HISTORY
        # ==================================================

        if selected_related_history:

            related_history_json = json.dumps(
                selected_related_history,
                ensure_ascii=False,
                default=str,
            )

            messages.append(
                {
                    "role": "system",
                    "content": (
                        "RELEVANT RELATED-CONCEPT HISTORY\n\n"
                        "These are historical interactions "
                        "selected because they are related "
                        "to the CURRENT QUESTION or its "
                        "concepts.\n\n"
                        "Use them when relevant to understand "
                        "the learner's prior performance, "
                        "misconceptions, strengths, or "
                        "knowledge gaps.\n\n"
                        f"{related_history_json}"
                    ),
                }
            )

        # ==================================================
        # 13. MEMORY POLICY
        # ==================================================

        messages.append(
            {
                "role": "system",
                "content": (
                    "MEMORY CONTEXT POLICY\n\n"
                    "Historical memory was selected "
                    "deterministically before this component "
                    "execution.\n"
                    f"Selected records: "
                    f"{memory_stats['selected_count']}\n"
                    f"History candidates: "
                    f"{memory_stats['history_candidates']}\n"
                    f"Related-history candidates: "
                    f"{memory_stats['related_history_candidates']}\n"
                    f"Estimated memory tokens after selection: "
                    f"{memory_stats['estimated_tokens_after']}\n\n"
                    "Use only the supplied historical evidence. "
                    "Do not invent historical facts."
                ),
            }
        )

        # ==================================================
        # 14. TASK INPUTS
        # ==================================================

        for node_id, artifact in context.inputs.items():

            messages.append(
                {
                    "role": "system",
                    "content": (
                        "TASK INPUT\n\n"
                        f"Source: {node_id}\n"
                        f"Type: {artifact.type}\n"
                        f"Title: {artifact.title}\n\n"
                        f"{artifact.content}"
                    ),
                }
            )

        return messages

    # ======================================================
    # SERIALIZATION
    # ======================================================

    @staticmethod
    def _serialize(
        value: Any,
    ) -> str:

        if isinstance(
            value,
            str,
        ):
            return value

        return json.dumps(
            value,
            ensure_ascii=False,
            default=str,
        )