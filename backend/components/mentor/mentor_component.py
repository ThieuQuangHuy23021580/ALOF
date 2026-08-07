from __future__ import annotations

from backend.application.services.llm_service import LLMService
from backend.core.component import Component
from backend.core.component_context import ComponentContext
from backend.core.component_result import ComponentResult
from backend.core.json_parser import JsonParser
from backend.domain.artifact.artifact_payload import ArtifactPayload
from backend.domain.artifact.artifact_type import ArtifactType
from backend.domain.artifact.factory import ArtifactFactory
from backend.infrastructure.prompts.context_builder import ContextBuilder
from backend.infrastructure.prompts.manager import PromptManager


class MentorComponent(Component):
    """
    Component responsible for explaining concepts
    and guiding learners.
    """

    component_id = "mentor"

    name = "Mentor"

    description = (
        "Explain concepts and guide learners."
    )

    def __init__(
        self,
    ) -> None:

        self._llm = LLMService()

        self._parser = JsonParser(
            ArtifactPayload,
        )

    def execute(
        self,
        context: ComponentContext,
    ) -> ComponentResult:

        system_prompt = PromptManager.get(
            self.component_id,
        )

        messages = ContextBuilder.build(
            context=context,
            system_prompt=system_prompt,
        )

        raw_response = self._llm.generate(
            messages,
        )

        payload = self._parser.parse(
            raw_response,
        )

        artifact = ArtifactFactory.create(
            type=ArtifactType.LESSON,
            producer=self.component_id,
            title=payload.title,
            content=payload.content,
            summary=payload.summary,
        )

        return ComponentResult(
            artifact=artifact,
        )