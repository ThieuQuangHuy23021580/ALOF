from __future__ import annotations

import traceback

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from backend.api.deps import get_learning_service
from backend.application.orchestration.execution_request_factory import (
    ExecutionRequestFactory,
)
from backend.application.services.learning_service import (
    LearningService,
)
from backend.domain.student.student import Student
from backend.schema import (
    ChatRequest,
    ChatResponse,
)


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


# ==========================================================
# Chat
# ==========================================================

@router.post(
    "/send",
    response_model=ChatResponse,
)
def send_message(
    request: ChatRequest,
    service: LearningService = Depends(
        get_learning_service,
    ),
) -> ChatResponse:
    """
    Execute a learning request through the ALOF pipeline.

    Pipeline:

        ChatRequest
            ↓
        ExecutionRequest
            ↓
        LearningService
            ↓
        LearningOrchestrator
            ↓
        Router
            ↓
        Planner
            ↓
        WorkflowBuilder
            ↓
        Runtime
            ↓
        RuntimeResult
    """

    try:

        # ==================================================
        # 1. Build domain Student
        # ==================================================

        student = Student(
            id=request.user_id,
            display_name="Learner",
        )

        # ==================================================
        # 2. API Request → Application Request
        # ==================================================

        execution_request = (
            ExecutionRequestFactory.create(
                request=request,
                student=student,
            )
        )

        # ==================================================
        # 3. Execute ALOF
        # ==================================================

        result = service.execute(
            execution_request,
        )

        # ==================================================
        # 4. Extract final response
        # ==================================================

        final_response = ""

        if result.final_artifact is not None:
            final_response = (
                result.final_artifact.content
            )

        # ==================================================
        # 5. Extract executed components
        # ==================================================

        executed_components = list(
            result.execution_order,
        )

        # ==================================================
        # 6. Build metadata
        # ==================================================

        metadata = dict(
            result.metadata,
        )

        metadata.update(
            {
                "status": result.status.value,
                "duration": result.duration,
                "execution_count": (
                    result.execution_count
                ),
                "artifact_count": (
                    result.artifact_count
                ),
            }
        )

        # ==================================================
        # 7. Return API response
        # ==================================================

        return ChatResponse(
            success=True,
            session_id=request.session_id,
            response=final_response,
            executed_components=executed_components,
            metadata=metadata,
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except HTTPException:
        raise

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )