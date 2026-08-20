from __future__ import annotations

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

    Responsible for connecting:

    Routing
        ->
    Planning
        ->
    Workflow Building
        ->
    Runtime Execution
    """

    def __init__(
        self,
        router: Router,
        planner: Planner,
        workflow_builder: WorkflowBuilder,
        runtime: Runtime,
    ) -> None:

        self._router = router
        self._planner = planner
        self._workflow_builder = workflow_builder
        self._runtime = runtime

    def execute(
        self,
        request: ExecutionRequest,
    ) -> RuntimeResult:

        # ==================================================
        # Routing
        # ==================================================

        routing_result = self._router.route(
            request.student,
            request.message,
        )

        # ==================================================
        # Planning
        # ==================================================

        planning_request = PlanningRequest(
            student=request.student,
            message=request.message,
            routing=routing_result,
            learning_state=request.learning_state,

        )

        plan = self._planner.plan(
            planning_request,
        )

        # ==================================================
        # Workflow
        # ==================================================

        workflow = self._workflow_builder.build(
            plan,
        )

        # ==================================================
        # Runtime
        # ==================================================

        context = RuntimeContext.from_student(
            workflow=workflow,
            student=request.student,
        )
        
        context.learning_state = request.learning_state

        context.set_metadata(
            "message",
            request.message,
        )

        context.set_metadata(
            "routing",
            routing_result.model_dump(),
        )

        return self._runtime.run(
            context,
        )