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
from backend.application.services.llm_service import (
    LLMService,
)
from backend.core.component_bootstrap import register_components
from backend.infrastructure.providers.groq_provider import (
    GroqProvider,
)


def create_learning_orchestrator() -> LearningOrchestrator:
    register_components()

    provider = GroqProvider()

    llm_service = LLMService(
        provider=provider,
    )

    router = LLMRouter()

    planner = SequentialPlanner()

    workflow_builder = SequentialWorkflowBuilder()

    runtime = SequentialRuntime(
        dependencies={
            "llm": llm_service,
        },
    )

    return LearningOrchestrator(
        router=router,
        planner=planner,
        workflow_builder=workflow_builder,
        runtime=runtime,
    )