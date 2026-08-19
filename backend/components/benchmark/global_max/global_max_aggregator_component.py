from __future__ import annotations

from backend.core.component import Component
from backend.core.component_context import ComponentContext
from backend.core.component_result import ComponentResult
from backend.domain.artifact.artifact import Artifact
from backend.domain.artifact.artifact_type import ArtifactType


class GlobalMaxAggregatorComponent(Component):
    """
    Aggregates local maxima produced by previous components.
    """

    component_id = "benchmark.global_max_aggregator"

    name = "SILO-BENCH Global Max Aggregator"

    description = (
        "Aggregates local maxima into one global maximum."
    )

    version = "1.0.0"

    def execute(
        self,
        context: ComponentContext,
    ) -> ComponentResult:

        values = context.get_input(
            "local_maxima",
        )

        if not isinstance(
            values,
            list,
        ):
            raise ValueError(
                "local_maxima must be a list."
            )

        if not values:
            raise ValueError(
                "local_maxima cannot be empty."
            )

        global_max = max(
            values,
        )

        artifact = Artifact(
            type=ArtifactType.RESEARCH,
            title="Global Maximum",
            content=str(global_max),
            producer=self.component_id,
            summary=(
                f"Global maximum: {global_max}"
            ),
            metadata={
                "operation": "global_max",
                "local_maxima": values,
            },
        )

        return ComponentResult(
            artifact=artifact,
            metadata={
                "global_max": global_max,
            },
        )