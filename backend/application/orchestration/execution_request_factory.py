from __future__ import annotations

from backend.domain.student.student import Student
from backend.schema.chat import ChatRequest

from .execution_request import ExecutionRequest


class ExecutionRequestFactory:
    """
    Creates an application-level ExecutionRequest
    from an API-level ChatRequest.
    """

    @staticmethod
    def create(
        request: ChatRequest,
        student: Student,
    ) -> ExecutionRequest:

        return ExecutionRequest(
            student=student,
            message=request.content,
            metadata={
                "session_id": request.session_id,
                "user_id": request.user_id,
                "mode": request.mode.value,
                "agent": request.agent,
            },
        )