from __future__ import annotations

from backend.application.services.adaptive_models import (
    ConceptEvidence,
    RetrievedMemory,
)


def _normalize(
    values: list[str],
) -> set[str]:
    return {
        str(value).strip().lower()
        for value in values
        if value is not None
        and str(value).strip()
    }


class EvidenceAggregator:
    """
    Convert retrieved memories into concept-level evidence.

    Multi-concept interactions distribute their retrieval
    weight across the relevant concepts.
    """

    def aggregate(
        self,
        memories: list[RetrievedMemory],
        target_concept_ids: list[str] | None = None,
    ) -> dict[str, ConceptEvidence]:

        target_ids = _normalize(
            target_concept_ids or []
        )

        result: dict[
            str,
            ConceptEvidence,
        ] = {}

        for memory in memories:

            history_ids = _normalize(
                memory.concept_ids
            )

            if target_ids:
                relevant_ids = (
                    history_ids & target_ids
                )
            else:
                relevant_ids = history_ids

            if not relevant_ids:
                continue

            share = (
                memory.retrieval_score
                / len(relevant_ids)
            )

            for concept_id in relevant_ids:

                evidence = result.get(
                    concept_id
                )

                if evidence is None:
                    evidence = ConceptEvidence(
                        concept_id=concept_id
                    )
                    result[concept_id] = evidence

                evidence.attempts += 1

                if memory.correct:
                    evidence.correct_count += 1
                    evidence.weighted_correct += (
                        share
                    )
                else:
                    evidence.incorrect_count += 1

                evidence.total_weight += share
                evidence.retrieval_weight += (
                    memory.retrieval_score
                )

                if (
                    memory.interaction_id
                    not in evidence
                    .evidence_interaction_ids
                ):
                    evidence.evidence_interaction_ids.append(
                        memory.interaction_id
                    )

        for evidence in result.values():
            evidence.finalize()

        return result