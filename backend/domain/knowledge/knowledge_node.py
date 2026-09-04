from __future__ import annotations
from uuid import uuid4

from pydantic import BaseModel, Field

from backend.domain.knowledge.knowledge_level import (
    KnowledgeLevel,
)


class KnowledgeNode(BaseModel):
    """
    Represents a single knowledge unit.

    A KnowledgeNode is the smallest learning object
    that can be planned, taught and assessed.
    """

    id: str = Field(
          default_factory=lambda: str(uuid4()),
        )

    title: str

    description: str = ""

    level: KnowledgeLevel = KnowledgeLevel.BEGINNER

    prerequisites: list[str] = Field(
        default_factory=list,
    )

    tags: list[str] = Field(
        default_factory=list,
    )

    def add_prerequisite(
        self,
        node_id: str,
    ) -> None:

        if node_id not in self.prerequisites:
            self.prerequisites.append(
                node_id,
            )

    def add_tag(
        self,
        tag: str,
    ) -> None:

        if tag not in self.tags:
            self.tags.append(
                tag,
            )