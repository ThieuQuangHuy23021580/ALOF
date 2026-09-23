from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from backend.infrastructure.database import get_db
from backend.infrastructure.database.models import ArtifactModel
from backend.infrastructure.database.repository import ALOFRepository

from .schemas import (
    ApiHealthResponse,
    JourneyResponse,
    LearningMessageRequest,
    LearningMessageResponse,
    LearningRequest,
    LearningSessionResponse,
    LedgerResponse,
    PreferenceUpdate,
    SessionsResponse,
)


api_router = APIRouter(
    prefix="/api/v1",
)


def get_repository(
    db: Session = Depends(get_db),
) -> ALOFRepository:
    return ALOFRepository(db)


def get_student_or_404(
    student_id: str,
    repo: ALOFRepository,
):
    student = repo.get_student(student_id)

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found.",
        )

    return student


def _message_response(
    message,
) -> LearningMessageResponse:
    return LearningMessageResponse(
        id=message.id,
        role=message.role,
        content=message.content,
        created_at=message.created_at,
    )


# ----------------------------------------------------------------------
# Health
# ----------------------------------------------------------------------

@api_router.get(
    "/health",
    response_model=ApiHealthResponse,
)
def health() -> ApiHealthResponse:
    return ApiHealthResponse(
        status="ok",
        service="ALOF Backend",
        version="v1",
    )


# ----------------------------------------------------------------------
# Student
# ----------------------------------------------------------------------

@api_router.get(
    "/students/{student_id}",
)
def get_student(
    student_id: str,
    repo: ALOFRepository = Depends(get_repository),
):
    return get_student_or_404(
        student_id,
        repo,
    )


# ----------------------------------------------------------------------
# Journey
# ----------------------------------------------------------------------

@api_router.get(
    "/journey/{student_id}",
    response_model=JourneyResponse,
)
def get_journey(
    student_id: str,
    repo: ALOFRepository = Depends(get_repository),
) -> JourneyResponse:

    get_student_or_404(
        student_id,
        repo,
    )

    return JourneyResponse(
        goal=jsonable_encoder(
            repo.get_goal(student_id)
        ),
        diagnosis=jsonable_encoder(
            repo.get_diagnosis(student_id)
        ),
        evidence=jsonable_encoder(
            repo.get_evidence(student_id)
        ),
        teaching_action=jsonable_encoder(
            repo.get_teaching_action(student_id)
        ),
        artifacts=jsonable_encoder(
            repo.get_artifacts(student_id)
        ),
    )


# ----------------------------------------------------------------------
# Sessions
# ----------------------------------------------------------------------

@api_router.get(
    "/sessions/{student_id}",
    response_model=SessionsResponse,
)
def get_sessions(
    student_id: str,
    repo: ALOFRepository = Depends(get_repository),
) -> SessionsResponse:

    get_student_or_404(
        student_id,
        repo,
    )

    sessions = repo.get_sessions(student_id)

    encoded_sessions = jsonable_encoder(
        sessions
    )

    return SessionsResponse(
        current_session=(
            encoded_sessions[0]
            if encoded_sessions
            else None
        ),
        history=encoded_sessions,
    )


# ----------------------------------------------------------------------
# Ledger
# ----------------------------------------------------------------------

@api_router.get(
    "/ledger/{student_id}",
    response_model=LedgerResponse,
)
def get_ledger(
    student_id: str,
    repo: ALOFRepository = Depends(get_repository),
) -> LedgerResponse:

    get_student_or_404(
        student_id,
        repo,
    )

    return LedgerResponse(
        diagnosis=jsonable_encoder(
            repo.get_diagnosis(student_id)
        ),
        evidence=jsonable_encoder(
            repo.get_evidence(student_id)
        ),
    )


# ----------------------------------------------------------------------
# Preferences
# ----------------------------------------------------------------------

@api_router.get(
    "/preferences/{student_id}",
)
def get_preferences(
    student_id: str,
    repo: ALOFRepository = Depends(get_repository),
):
    get_student_or_404(
        student_id,
        repo,
    )

    preference = repo.get_preference(
        student_id
    )

    if preference is None:
        raise HTTPException(
            status_code=404,
            detail="Learning preference not found.",
        )

    return preference


@api_router.put(
    "/preferences/{student_id}",
)
def update_preferences(
    student_id: str,
    request: PreferenceUpdate,
    repo: ALOFRepository = Depends(get_repository),
):
    get_student_or_404(
        student_id,
        repo,
    )

    return repo.update_preference(
        student_id=student_id,
        data=request.model_dump(),
    )


# ----------------------------------------------------------------------
# Current learning session
# ----------------------------------------------------------------------

@api_router.get(
    "/learning-sessions/{student_id}",
    response_model=LearningSessionResponse,
)
def get_current_learning_session(
    student_id: str,
    repo: ALOFRepository = Depends(get_repository),
) -> LearningSessionResponse:

    get_student_or_404(
        student_id,
        repo,
    )

    session = repo.get_latest_session(
        student_id
    )

    if session is not None:
        messages = repo.get_session_messages(
            session.id
        )

        return LearningSessionResponse(
            session_id=session.id,
            request=session.request,
            messages=[
                _message_response(message)
                for message in messages
            ],
            artifacts=jsonable_encoder(
                repo.get_artifacts(student_id)
            ),
            diagnosis=jsonable_encoder(
                repo.get_diagnosis(student_id)
            ),
            teaching_action=jsonable_encoder(
                repo.get_teaching_action(student_id)
            ),
            evidence=jsonable_encoder(
                repo.get_evidence(student_id)
            ),
            created_at=session.created_at,
        )

    return LearningSessionResponse(
        session_id="",
        request="",
        messages=[],
        artifacts=jsonable_encoder(
            repo.get_artifacts(student_id)
        ),
        diagnosis=jsonable_encoder(
            repo.get_diagnosis(student_id)
        ),
        teaching_action=jsonable_encoder(
            repo.get_teaching_action(student_id)
        ),
        evidence=jsonable_encoder(
            repo.get_evidence(student_id)
        ),
        created_at=datetime.now(UTC),
    )


# ----------------------------------------------------------------------
# Create learning session
# ----------------------------------------------------------------------

@api_router.post(
    "/learning-sessions/{student_id}",
    response_model=LearningSessionResponse,
)
def create_learning_session(
    student_id: str,
    request: LearningRequest,
    repo: ALOFRepository = Depends(get_repository),
) -> LearningSessionResponse:

    get_student_or_404(
        student_id,
        repo,
    )

    session_id = str(uuid4())
    user_message_id = str(uuid4())
    assistant_message_id = str(uuid4())
    artifact_id = str(uuid4())

    now = datetime.now(UTC)

    session = repo.create_session(
        student_id=student_id,
        session_id=session_id,
        request=request.question,
        created_at=now,
    )

    # User message
    user_message = repo.create_message(
        session_id=session.id,
        message_id=user_message_id,
        role="user",
        content=request.question,
        created_at=now,
    )

    # Current backend response.
    # This will later be replaced by the real ALOF Runtime/Orchestrator.
    assistant_content = (
        f"ALOF received your request: "
        f"{request.question}"
    )

    assistant_message = repo.create_message(
        session_id=session.id,
        message_id=assistant_message_id,
        role="assistant",
        content=assistant_content,
        created_at=datetime.now(UTC),
    )

    artifact = ArtifactModel(
        id=artifact_id,
        type="response",
        title="ALOF Response",
        content=assistant_content,
        producer="mentor",
        summary="Generated learning response.",
        metadata_json="{}",
        created_at=datetime.now(UTC),
    )

    repo.db.add(artifact)
    repo.db.commit()
    repo.db.refresh(artifact)

    return LearningSessionResponse(
        session_id=session.id,
        request=session.request,
        messages=[
            _message_response(user_message),
            _message_response(assistant_message),
        ],
        artifacts=jsonable_encoder(
            [artifact]
        ),
        diagnosis=jsonable_encoder(
            repo.get_diagnosis(student_id)
        ),
        teaching_action=jsonable_encoder(
            repo.get_teaching_action(student_id)
        ),
        evidence=jsonable_encoder(
            repo.get_evidence(student_id)
        ),
        created_at=session.created_at,
    )


# ----------------------------------------------------------------------
# Append message to existing session
# ----------------------------------------------------------------------

@api_router.post(
    "/learning-sessions/{student_id}/{session_id}/messages",
    response_model=LearningSessionResponse,
)
def create_learning_message(
    student_id: str,
    session_id: str,
    request: LearningMessageRequest,
    repo: ALOFRepository = Depends(get_repository),
) -> LearningSessionResponse:

    get_student_or_404(
        student_id,
        repo,
    )

    session = repo.get_session(
        student_id=student_id,
        session_id=session_id,
    )

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Learning session not found.",
        )

    now = datetime.now(UTC)

    repo.create_message(
        session_id=session.id,
        message_id=str(uuid4()),
        role="user",
        content=request.content,
        created_at=now,
    )

    # Current backend response.
    # This will later be replaced by the real ALOF Runtime/Orchestrator.
    assistant_content = (
        f"ALOF received your request: "
        f"{request.content}"
    )

    repo.create_message(
        session_id=session.id,
        message_id=str(uuid4()),
        role="assistant",
        content=assistant_content,
        created_at=datetime.now(UTC),
    )

    messages = repo.get_session_messages(
        session.id
    )

    return LearningSessionResponse(
        session_id=session.id,
        request=session.request,
        messages=[
            _message_response(message)
            for message in messages
        ],
        artifacts=jsonable_encoder(
            repo.get_artifacts(student_id)
        ),
        diagnosis=jsonable_encoder(
            repo.get_diagnosis(student_id)
        ),
        teaching_action=jsonable_encoder(
            repo.get_teaching_action(student_id)
        ),
        evidence=jsonable_encoder(
            repo.get_evidence(student_id)
        ),
        created_at=session.created_at,
    )
