from __future__ import annotations

from backend.application.orchestration.learning_orchestrator import (
    LearningOrchestrator,
)
from backend.application.planning.sequential_planner import (
    SequentialPlanner,
)
from backend.application.planning.sequential_workflow_builder import (
    SequentialWorkflowBuilder,
)
from backend.application.routing.llm_router import (
    LLMRouter,
)
from backend.application.runtime.sequential_runtime import (
    SequentialRuntime,
)
from backend.core.component_bootstrap import (
    register_components,
)


class ApplicationFactory:
    """
    Composition root for the learning application.

    Responsible for assembling application-level
    dependencies and infrastructure.

    It does not contain business logic.
    """

    @staticmethod
    def create_orchestrator() -> LearningOrchestrator:
        # ======================================================
        # Components
        # ======================================================

        register_components()

        # ======================================================
        # Application Pipeline
        # ======================================================

        router = LLMRouter()

        planner = SequentialPlanner()

        workflow_builder = (
            SequentialWorkflowBuilder()
        )

        runtime = SequentialRuntime()

        # ======================================================
        # Orchestrator
        # ======================================================

        return LearningOrchestrator(
            router=router,
            planner=planner,
            workflow_builder=workflow_builder,
            runtime=runtime,
        )