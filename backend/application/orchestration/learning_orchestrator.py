from __future__ import annotations

from backend.application.orchestration.adaptive_learning_pipeline import (
    AdaptiveLearningPipeline,
)
from backend.application.orchestration.adaptive_learning_result import (
    AdaptiveLearningResult,
)
from backend.application.orchestration.execution_request import (
    ExecutionRequest,
)
from backend.application.planning.planner import Planner
from backend.application.planning.planning_request import (
    PlanningRequest,
)
from backend.application.planning.workflow_builder import (
    WorkflowBuilder,
)
from backend.application.routing.router import Router
from backend.application.runtime.runtime import Runtime
from backend.application.runtime.runtime_context import (
    RuntimeContext,
)
from backend.application.runtime.runtime_result import (
    RuntimeResult,
)


class LearningOrchestrator:
    """
    Application-level coordinator.

    Coordinates the complete learning execution pipeline:

        ExecutionRequest
            ↓
        Routing
            ↓
        Adaptive Learning
            ↓
        Planning
            ↓
        Workflow Building
            ↓
        Runtime Execution
            ↓
        RuntimeResult
    """

    def __init__(
        self,
        router: Router,
        planner: Planner,
        workflow_builder: WorkflowBuilder,
        runtime: Runtime,
        adaptive_learning_pipeline: AdaptiveLearningPipeline | None = None,
    ) -> None:

        self._router = router
        self._planner = planner
        self._workflow_builder = workflow_builder
        self._runtime = runtime

        self._adaptive_learning_pipeline = (
            adaptive_learning_pipeline
            if adaptive_learning_pipeline is not None
            else AdaptiveLearningPipeline()
        )

    def execute(
        self,
        request: ExecutionRequest,
    ) -> RuntimeResult:

        # ==================================================
        # 1. ROUTING
        # ==================================================

        routing_result = self._router.route(
            request.student,
            request.message,
        )

        # ==================================================
        # 2. CURRENT QUESTION / CONCEPTS
        # ==================================================

        current_question = request.metadata.get(
            "current_question",
            request.message,
        )

        current_concept_ids = request.metadata.get(
            "current_concept_ids",
            [],
        )

        # Defensive normalization.
        if not isinstance(
            current_concept_ids,
            list,
        ):
            current_concept_ids = []

        # ==================================================
        # 3. ADAPTIVE LEARNING
        # ==================================================

        adaptive_learning: AdaptiveLearningResult = (
            self._adaptive_learning_pipeline.run(
                learning_state=request.learning_state,
                current_question=current_question,
                related_concept_ids=current_concept_ids,
                primary_concept_ids=current_concept_ids,
            )
        )

        # ==================================================
        # 4. PLANNING
        # ==================================================

        planning_request = PlanningRequest(
            student=request.student,
            message=request.message,
            routing=routing_result,
            learning_state=request.learning_state,
            adaptive_learning=adaptive_learning,
        )

        plan = self._planner.plan(
            planning_request,
        )

        # ==================================================
        # 5. WORKFLOW BUILDING
        # ==================================================

        workflow = self._workflow_builder.build(
            plan,
        )

        # ==================================================
        # 6. RUNTIME CONTEXT
        # ==================================================

        context = RuntimeContext(
            workflow=workflow,
            learning_state=request.learning_state,
            adaptive_learning=adaptive_learning,
        )

        context.set_metadata(
            "student_id",
            request.student.id,
        )

        context.set_metadata(
            "message",
            request.message,
        )

        context.set_metadata(
            "current_question",
            current_question,
        )

        context.set_metadata(
            "current_concept_ids",
            current_concept_ids,
        )

        context.set_metadata(
            "routing",
            routing_result.model_dump(),
        )

        # ==================================================
        # 7. DEBUG
        # ==================================================

        print(
            "ROUTING:",
            routing_result.model_dump(),
        )

        print(
            "CURRENT QUESTION:",
            current_question,
        )

        print(
            "CURRENT CONCEPTS:",
            current_concept_ids,
        )

        print(
            "ADAPTIVE LEARNING:",
            adaptive_learning.model_dump(),
        )

        print(
            "PLAN:",
            plan.model_dump(),
        )

        print(
            "WORKFLOW NODES:",
            [
                {
                    "id": node.id,
                    "component": node.component_id,
                    "objective": node.objective,
                    "action": node.action,
                    "strategy": node.strategy,
                    "difficulty": node.difficulty,
                    "focus_concepts": node.focus_concepts,
                }
                for node in workflow.nodes
            ],
        )

        # ==================================================
        # 8. RUNTIME EXECUTION
        # ==================================================

        return self._runtime.run(
            context,
        )