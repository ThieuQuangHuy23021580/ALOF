from __future__ import annotations

from backend.application.services.llm_service import (
    LLMService,
)
from backend.core.component import Component
from backend.core.component_context import ComponentContext
from backend.core.component_result import ComponentResult
from backend.core.json_parser import JsonParser
from backend.domain.artifact.artifact_payload import (
    ArtifactPayload,
)
from backend.domain.artifact.artifact_type import (
    ArtifactType,
)
from backend.domain.artifact.factory import (
    ArtifactFactory,
)
from backend.infrastructure.prompts.context_builder import (
    ContextBuilder,
)
from backend.infrastructure.prompts.manager import (
    PromptManager,
)


class QuizComponent(Component):
    """
    Component responsible for generating
    adaptive quizzes for learners.
    """

    component_id = "quiz"

    name = "Quiz"

    description = (
        "Generate adaptive quizzes "
        "for learners."
    )

    def __init__(
        self,
    ) -> None:

        self._parser = JsonParser(
            ArtifactPayload,
        )

        self._context_builder = ContextBuilder()

    def execute(
        self,
        context: ComponentContext,
    ) -> ComponentResult:

        # ======================================================
        # LLM Dependency
        # ======================================================

        llm = context.get_dependency(
            "llm",
        )

        if not isinstance(
            llm,
            LLMService,
        ):
            raise TypeError(
                "QuizComponent requires "
                "an LLMService dependency "
                "under key 'llm'."
            )

        # ======================================================
        # Prompt
        # ======================================================

        system_prompt = PromptManager.get(
            self.component_id,
        )

        messages = self._context_builder.build(
            context=context,
            system_prompt=system_prompt,
        )

        # ======================================================
        # Real LLM
        # ======================================================

        raw_response = llm.generate(
            messages,
            stage="runtime",
            component="quiz",
        )

        # ======================================================
        # Parse
        # ======================================================

        payload = self._parser.parse(
            raw_response,
        )

        # ======================================================
        # Artifact
        # ======================================================

        artifact = ArtifactFactory.create(
            type=ArtifactType.QUIZ,
            producer=self.component_id,
            title=payload.title,
            content=payload.content,
            summary=payload.summary,
        )

        return ComponentResult(
            artifact=artifact,
        )