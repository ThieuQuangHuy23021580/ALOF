from __future__ import annotations

from backend.application.services.llm_service import (
    LLMService,
)
from backend.core.component import Component
from backend.core.component_context import ComponentContext
from backend.core.component_result import ComponentResult
from backend.core.dependency_context import DependencyContext
from backend.core.json_parser import JsonParser
from backend.domain.artifact.artifact import Artifact
from backend.domain.artifact.artifact_type import ArtifactType
from backend.infrastructure.prompts.context_builder import (
    ContextBuilder,
)
from backend.infrastructure.prompts.manager import (
    PromptManager,
)
from backend.domain.artifact.artifact_payload import ArtifactPayload


class PlannerComponent(Component):
    """
    Learning component responsible for creating
    learning plans from the current task.
    """

    component_id = "planner"

    name = "Planner"

    description = (
        "Creates structured learning plans "
        "from the current task and available inputs."
    )

    def execute(
        self,
        context: ComponentContext,
    ) -> ComponentResult:

        # ======================================================
        # Dependency
        # ======================================================

        llm = context.dependencies.get(
            "llm",
        )

        if not isinstance(
            llm,
            LLMService,
        ):
            raise TypeError(
                "PlannerComponent requires "
                "an LLMService dependency."
            )

        # ======================================================
        # Prompt
        # ======================================================

        system_prompt = PromptManager.get(
            "planner",
        )

        # ======================================================
        # Context
        # ======================================================

        messages = ContextBuilder.build(
            context=context,
            system_prompt=system_prompt,
        )

        # ======================================================
        # LLM
        # ======================================================

        raw_response = llm.generate(
            messages,
        )

        # ======================================================
        # Parse
        # ======================================================

        parser = JsonParser(
            ArtifactPayload,
        )

        payload = parser.parse(
            raw_response,
        )

        # ======================================================
        # Artifact
        # ======================================================

        artifact = Artifact(
            type=ArtifactType.ROADMAP,
            title=payload.title,
            content=payload.content,
            summary=payload.summary,
            producer=self.component_id,
        )

        return ComponentResult(
            artifact=artifact,
        )