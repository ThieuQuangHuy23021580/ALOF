from __future__ import annotations

import logging

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

logger = logging.getLogger(__name__)


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

        self._context_builder = ContextBuilder()

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

        messages = self._context_builder.build(
            context=context,
            system_prompt=system_prompt,
        )

        request_message = context.runtime.metadata.get(
            "message",
            "",
        )

        if request_message:
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "CURRENT QUESTION / ORIGINAL REQUEST\n\n"
                        f"{request_message}\n\n"
                    ),
                }
            )

        raw_response = llm.generate(
            messages,
            stage="runtime",
            component="mentor",
        )

        logger.debug(
            "Mentor raw response received: %d chars",
            len(raw_response),
        )

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

        logger.debug(
            "Mentor payload parsed: title=%r content_chars=%d summary_chars=%d",
            payload.title,
            len(payload.content),
            len(payload.summary),
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