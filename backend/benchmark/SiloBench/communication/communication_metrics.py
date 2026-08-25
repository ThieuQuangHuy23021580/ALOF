from __future__ import annotations

from typing import Any

from .communication_trace import CommunicationTrace


class CommunicationMetrics:
    """
    Computes SILO-BENCH communication metrics.
    """

    @staticmethod
    def redundancy_ratio(
        trace: CommunicationTrace,
        optimal_message_count: int,
    ) -> float:

        if optimal_message_count <= 0:
            raise ValueError(
                "optimal_message_count must be positive."
            )

        return (
            trace.message_count
            / optimal_message_count
        )

    @staticmethod
    def topological_fidelity(
        trace: CommunicationTrace,
        optimal_edges: set[tuple[int, int]],
    ) -> float:

        empirical_edges = trace.edges

        union = (
            empirical_edges
            | optimal_edges
        )

        if not union:
            return 1.0

        intersection = (
            empirical_edges
            & optimal_edges
        )

        return (
            len(intersection)
            / len(union)
        )

    @staticmethod
    def build(
        *,
        trace: CommunicationTrace,
        optimal_message_count: int,
        optimal_edges: set[tuple[int, int]],
    ) -> dict[str, Any]:

        return {
            "communication_messages": (
                trace.message_count
            ),
            "rounds": trace.rounds,
            "communication_redundancy_ratio": (
                CommunicationMetrics.redundancy_ratio(
                    trace,
                    optimal_message_count,
                )
            ),
            "topological_fidelity": (
                CommunicationMetrics.topological_fidelity(
                    trace,
                    optimal_edges,
                )
            ),
        }