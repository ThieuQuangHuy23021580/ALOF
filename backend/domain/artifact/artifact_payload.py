from __future__ import annotations

from pydantic import BaseModel


class ArtifactPayload(BaseModel):
    """
    Structured LLM output before converting
    into a domain Artifact.
    """

    title: str = ""

    content: str

    summary: str = ""