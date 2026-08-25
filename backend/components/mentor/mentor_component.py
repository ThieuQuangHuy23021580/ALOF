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

    Runtime dependencies are resolved through
    ComponentContext.
    """

    component_id = "mentor"

    name = "Mentor"

    description = (
        "Explain concepts and guide learners."
    )

    def __init__(
        self,
    ) -> None:

        self._parser = JsonParser(
            ArtifactPayload,
        )

    def execute(
        self,
        context: ComponentContext,
    ) -> ComponentResult:

        llm = context.get_dependency(
            "llm",
        )

        if not isinstance(
            llm,
            LLMService,
        ):
            raise TypeError(
                "MentorComponent requires "
                "an LLMService dependency "
                "under key 'llm'."
            )

        system_prompt = PromptManager.get(
            self.component_id,
        )

        messages = ContextBuilder.build(
            context=context,
            system_prompt=system_prompt,
        )

        # LongTutor / current learning request.
        request_message = context.runtime.metadata.get(
            "message",
            "",
        )

        if request_message:
            messages.append(
                {
                    "role": "user",
                    "content": request_message,
                }
            )

        raw_response = llm.generate(
            messages,
            stage="runtime",
            component="mentor",
        )

        print("\n===== MENTOR RAW RESPONSE =====")
        print(raw_response)
        print("================================\n")

        try:
            payload = self._parser.parse(
                raw_response,
            )
        except (ValueError, TypeError):
            payload = ArtifactPayload(
                title="Mentor Response",
                content=raw_response,
                summary="",
            )

        print("\n===== MENTOR PAYLOAD =====")
        print(payload.model_dump())
        print("==========================\n")

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