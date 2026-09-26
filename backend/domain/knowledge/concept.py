from __future__ import annotations

from pydantic import BaseModel, Field


class Concept(BaseModel):
    """
    Canonical knowledge concept identity.

    The concept registry is the source of truth for
    concept_id values. Downstream services must not
    invent new canonical IDs.
    """

    concept_id: str
    name: str
    description: str = ""
    domain: str = ""
    parent_concept_id: str | None = None
    difficulty: str | None = None
    status: str = "active"
    aliases: list[str] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)
