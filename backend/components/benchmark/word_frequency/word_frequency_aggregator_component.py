from __future__ import annotations

from backend.core.component import Component
from backend.core.component_context import ComponentContext
from backend.core.component_result import ComponentResult
from backend.domain.artifact.artifact import Artifact
from backend.domain.artifact.artifact_type import ArtifactType


class WordFrequencyAggregatorComponent(Component):
    """
    Aggregates local word-frequency counts.
    """

    component_id = (
        "benchmark.word_frequency_aggregator"
    )

    name = "SILO-BENCH Word Frequency Aggregator"

    description = (
        "Aggregates local word-frequency counts "
        "into one global count."
    )

    version = "1.0.0"

    def execute(
        self,
        context: ComponentContext,
    ) -> ComponentResult:

        values = context.get_input(
            "local_counts",
        )

        if not isinstance(
            values,
            list,
        ):
            raise ValueError(
                "local_counts must be a list."
            )

        if not values:
            raise ValueError(
                "local_counts cannot be empty."
            )

        if not all(
            isinstance(value, int)
            for value in values
        ):
            raise TypeError(
                "local_counts must contain integers."
            )

        total_count = sum(
            values,
        )

        artifact = Artifact(
            type=ArtifactType.RESEARCH,
            title="Word Frequency",
            content=str(total_count),
            producer=self.component_id,
            summary=(
                f"Global word frequency: "
                f"{total_count}"
            ),
            metadata={
                "operation": "word_frequency",
                "local_counts": values,
            },
        )

        return ComponentResult(
            artifact=artifact,
            metadata={
                "total_count": total_count,
            },
        )