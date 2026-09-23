
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class LearningRequest(BaseModel):
    question: str
    student_id: str
    concept_ids: list[str] = Field(default_factory=list)


class LearningMessageRequest(BaseModel):
    content: str


class PreferenceUpdate(BaseModel):
    preferred_outputs: list[str] = Field(default_factory=list)
    preferred_difficulty: str = "adaptive"
    preferred_pace: str = "adaptive"
    session_duration_minutes: int = 30
    include_examples: bool = True
    include_quiz: bool = True
    include_flashcards: bool = True
    include_summary: bool = True


class ApiHealthResponse(BaseModel):
    status: str
    service: str
    version: str


class JourneyResponse(BaseModel):
    goal: Any | None = None
    diagnosis: Any | None = None
    evidence: Any | None = None
    teaching_action: Any | None = None
    artifacts: list[Any] = Field(default_factory=list)


class SessionsResponse(BaseModel):
    current_session: dict[str, Any] | None = None
    history: list[dict[str, Any]] = Field(default_factory=list)


class LedgerResponse(BaseModel):
    diagnosis: Any | None = None
    evidence: Any | None = None


class LearningMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime


class LearningSessionResponse(BaseModel):
    session_id: str
    request: str
    messages: list[LearningMessageResponse] = Field(
        default_factory=list
    )
    artifacts: list[Any] = Field(default_factory=list)
    diagnosis: Any | None = None
    teaching_action: Any | None = None
    evidence: Any | None = None
    workflow: Any | None = None
    created_at: datetime
