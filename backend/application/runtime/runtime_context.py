from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from backend.application.orchestration.adaptive_learning_result import (
    AdaptiveLearningResult,
)
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

from backend.domain.learning.adaptive_teaching_action import (
    AdaptiveTeachingAction,
)
from backend.domain.learning.historical_evidence import (
    HistoricalEvidence,
)
from backend.domain.learning.knowledge_diagnosis import (
    KnowledgeDiagnosis,
)

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

    historical_evidence: HistoricalEvidence | None = None

    knowledge_diagnosis: KnowledgeDiagnosis | None = None

    adaptive_teaching_action: AdaptiveTeachingAction | None = None

    adaptive_learning: AdaptiveLearningResult | None = None

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
    # Adaptive learning
    # ======================================================

    def set_adaptive_learning(
        self,
        result: AdaptiveLearningResult,
    ) -> None:
        """
        Store the complete adaptive-learning result and expose
        every intermediate stage for debugging / benchmarking.
        """

        self.adaptive_learning = result

        # Preserve intermediate objects inside RuntimeContext.
        self.historical_evidence = result.evidence
        self.knowledge_diagnosis = result.diagnosis
        self.adaptive_teaching_action = result.teaching_action

        # Expose JSON-serializable metadata for benchmark auditing.
        self.set_metadata(
            "historical_evidence",
            result.evidence.model_dump(mode="json"),
        )

        self.set_metadata(
            "knowledge_diagnosis",
            result.diagnosis.model_dump(mode="json"),
        )

        self.set_metadata(
            "adaptive_teaching_action",
            result.teaching_action.model_dump(mode="json"),
        )

        self.set_metadata(
            "adaptive_learning",
            result.model_dump(mode="json"),
        )

    def has_adaptive_learning(self) -> bool:
        """
        Return whether adaptive-learning analysis
        has been completed.
        """

        return self.adaptive_learning is not None

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

    # ======================================================
    # Adaptive learning
    # ======================================================

    def set_historical_evidence(
        self,
        evidence: HistoricalEvidence,
    ) -> None:

        self.historical_evidence = evidence

    def set_knowledge_diagnosis(
        self,
        diagnosis: KnowledgeDiagnosis,
    ) -> None:

        self.knowledge_diagnosis = diagnosis

    def set_adaptive_teaching_action(
        self,
        action: AdaptiveTeachingAction,
    ) -> None:

        self.adaptive_teaching_action = action

    def get_historical_evidence(
        self,
    ) -> HistoricalEvidence | None:

        return self.historical_evidence

    def get_knowledge_diagnosis(
        self,
    ) -> KnowledgeDiagnosis | None:

        return self.knowledge_diagnosis

    def get_adaptive_teaching_action(
        self,
    ) -> AdaptiveTeachingAction | None:

        return self.adaptive_teaching_action