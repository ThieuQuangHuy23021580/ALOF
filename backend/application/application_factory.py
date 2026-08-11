
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
from backend.application.routing.llm_intent_recognizer import (
    LLMIntentRecognizer,
)
from backend.application.routing.llm_router import (
    LLMRouter,
)
from backend.application.runtime.sequential_runtime import (
    SequentialRuntime,
)
from backend.application.runtime.sequential_scheduler import (
    SequentialScheduler,
)
from backend.application.services.llm_service import (
    LLMService,
)
from backend.core.component_bootstrap import (
    register_components,
)
from backend.core.default_component_executor import (
    DefaultComponentExecutor,
)


class ApplicationFactory:
    """
    Composition root for the learning application.

    Responsible for assembling application-level
    dependencies and infrastructure.

    It does not contain business logic.

    Dependency responsibilities
    ---------------------------
    - Application services receive their dependencies
      directly during construction.
    - Components receive runtime dependencies through
      ComponentContext / DependencyContext.
    """

    @staticmethod
    def create_orchestrator() -> LearningOrchestrator:

        # ======================================================
        # Components
        # ======================================================

        register_components()

        # ======================================================
        # Shared Services
        # ======================================================

        llm_service = LLMService()

        # ======================================================
        # Routing
        #
        # LLMIntentRecognizer is an application-level service.
        # Direct constructor injection is intentional here.
        # ======================================================

        intent_recognizer = LLMIntentRecognizer(
            llm=llm_service,
        )

        router = LLMRouter(
            recognizer=intent_recognizer,
        )

        # ======================================================
        # Planning
        # ======================================================

        planner = SequentialPlanner()

        # ======================================================
        # Workflow
        # ======================================================

        workflow_builder = (
            SequentialWorkflowBuilder()
        )

        # ======================================================
        # Runtime
        # ======================================================

        scheduler = SequentialScheduler()

        component_executor = (
            DefaultComponentExecutor()
        )

        # ======================================================
        # Runtime Dependencies
        #
        # These dependencies are NOT injected into Component
        # constructors.
        #
        # SequentialRuntime passes them to
        # ComponentContextBuilder, which creates a
        # DependencyContext for each Component execution.
        # ======================================================

        runtime = SequentialRuntime(
            scheduler=scheduler,
            executor=component_executor,
            dependencies={
                "llm": llm_service,
            },
        )

        # ======================================================
        # Orchestrator
        # ======================================================

        return LearningOrchestrator(
            router=router,
            planner=planner,
            workflow_builder=workflow_builder,
            runtime=runtime,
        )

