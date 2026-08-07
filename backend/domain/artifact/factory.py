from __future__ import annotations

from typing import Any

from backend.domain.artifact.artifact import Artifact
from backend.domain.artifact.artifact_type import ArtifactType


class ArtifactFactory:
    """
    Factory for creating Artifacts.

    Every Artifact inside ALOF should be created
    through this factory.
    """

    @staticmethod
    def create(
        *,
        type: ArtifactType,
        producer: str,
        content: str,
        title: str = "",
        summary: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> Artifact:

        return Artifact(
            type=type,
            producer=producer,
            title=title,
            content=content,
            summary=summary,
            metadata=metadata or {},
        )