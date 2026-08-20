from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from backend.application.runtime.component_execution import (
    ComponentExecution,
)
from backend.core.execution_status import ExecutionStatus
from backend.domain.artifact.artifact import Artifact
from backend.domain.learning.learning_state import (
    LearningState,
)
from backend.domain.student.student import Student
from backend.domain.workflow.workflow import Workflow


class RuntimeContext(BaseModel):
    """
    Holds the execution state of a workflow.

    RuntimeContext represents the learner-specific state
    of one workflow execution.
    """

    workflow: Workflow

    state: ExecutionStatus = ExecutionStatus.CREATED

    learning_state: LearningState = Field(
        default_factory=lambda: LearningState(
            learner_id="default",
        ),
    )

    current_node: str | None = None

    artifacts: dict[str, Artifact] = Field(
        default_factory=dict,
    )

    component_executions: dict[
        str,
        ComponentExecution,
    ] = Field(
        default_factory=dict,
    )

    execution_order: list[str] = Field(
        default_factory=list,
    )

    started_at: datetime | None = None

    finished_at: datetime | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    @classmethod
    def from_student(
        cls,
        workflow: Workflow,
        student: Student,
    ) -> RuntimeContext:
        """
        Create a learner-specific RuntimeContext.

        The RuntimeContext receives a snapshot of the
        learner's current progress and preferences for
        this execution.
        """

        learning_state = LearningState(
            learner_id=student.id,
            progress={
                "completed_topics": float(
                    student.learning_progress.completed_topics,
                ),
                "completed_sessions": float(
                    student.learning_progress.completed_sessions,
                ),
                "mastered_topics": float(
                    student.learning_progress.mastered_topics,
                ),
                "current_streak": float(
                    student.learning_progress.current_streak,
                ),
                "total_learning_minutes": float(
                    student.learning_progress.total_learning_minutes,
                ),
                "overall_mastery": (
                    student.learning_progress.overall_mastery
                ),
            },
            metadata={
                "display_name": student.display_name,
                "preferred_difficulty": (
                    student.learning_preference.preferred_difficulty
                ),
                "preferred_pace": (
                    student.learning_preference.preferred_pace
                ),
                "session_duration_minutes": (
                    student.learning_preference.session_duration_minutes
                ),
                "include_examples": (
                    student.learning_preference.include_examples
                ),
                "include_quiz": (
                    student.learning_preference.include_quiz
                ),
                "include_flashcards": (
                    student.learning_preference.include_flashcards
                ),
                "include_summary": (
                    student.learning_preference.include_summary
                ),
            },
        )

        return cls(
            workflow=workflow,
            learning_state=learning_state,
        )

    # ======================================================
    # Execution lifecycle
    # ======================================================

    def start_execution(
        self,
    ) -> None:

        self.started_at = datetime.now(
            UTC,
        )

    def finish_execution(
        self,
    ) -> None:

        self.finished_at = datetime.now(
            UTC,
        )

    def add_execution_step(
        self,
        node_id: str,
    ) -> None:

        self.execution_order.append(
            node_id,
        )

    def execution_duration(
        self,
    ) -> float | None:

        if (
            self.started_at is None
            or self.finished_at is None
        ):
            return None

        return (
            self.finished_at
            - self.started_at
        ).total_seconds()

    # ======================================================
    # Workflow state
    # ======================================================

    def set_current_node(
        self,
        node_id: str | None,
    ) -> None:

        self.current_node = node_id

    # ======================================================
    # Artifact management
    # ======================================================

    def add_artifact(
        self,
        node_id: str,
        artifact: Artifact,
    ) -> None:

        self.artifacts[node_id] = artifact

    def get_artifact(
        self,
        node_id: str,
    ) -> Artifact | None:

        return self.artifacts.get(
            node_id,
        )

    def has_artifact(
        self,
        node_id: str,
    ) -> bool:

        return node_id in self.artifacts

    # ======================================================
    # Metadata
    # ======================================================

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

    # ======================================================
    # Component execution
    # ======================================================

    def start_component_execution(
        self,
        node_id: str,
        component_id: str,
    ) -> None:

        execution = ComponentExecution(
            node_id=node_id,
            component_id=component_id,
        )

        execution.start()

        self.component_executions[node_id] = execution

    def complete_component_execution(
        self,
        node_id: str,
    ) -> None:

        execution = self.component_executions.get(
            node_id,
        )

        if execution is not None:
            execution.complete()

    def fail_component_execution(
        self,
        node_id: str,
        error: str,
    ) -> None:

        execution = self.component_executions.get(
            node_id,
        )

        if execution is not None:
            execution.fail(
                error,
            )