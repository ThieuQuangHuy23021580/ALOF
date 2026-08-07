from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from backend.domain.artifact.artifact_type import ArtifactType
from pydantic import BaseModel, Field


class Artifact(BaseModel):
    """
    Aggregate Root của toàn bộ output trong ALOF.

    Mọi Component đều tạo ra đúng một Artifact.
    """

    id: str = Field(
        default_factory=lambda: str(uuid4()),
    )

    type: ArtifactType

    title: str = ""

    content: str

    producer: str

    summary: str = ""

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(
            UTC,
        ),
    )

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.metadata.get(
            key,
            default,
        )

    def has_metadata(
        self,
        key: str,
    ) -> bool:

        return key in self.metadata