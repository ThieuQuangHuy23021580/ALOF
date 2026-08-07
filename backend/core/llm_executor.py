from __future__ import annotations

from typing import Any
from typing import TypeVar

from pydantic import BaseModel

from backend.core.parser import Parser
from backend.infrastructure.prompts.renderer import PromptRenderer
from backend.infrastructure.providers.llm_provider import (
    LLMProvider,
)

T = TypeVar(
    "T",
    bound=BaseModel,
)


class LLMExecutor:
    """
    Coordinates prompt rendering, LLM invocation and
    response parsing.

    This class contains no business logic.
    """

    def __init__(
        self,
        provider: LLMProvider,
        renderer: PromptRenderer,
    ) -> None:

        self._provider = provider
        self._renderer = renderer

    def execute(
        self,
        *,
        template: str,
        values: dict[str, Any],
        parser: Parser[T],
    ) -> T:

        prompt = self._renderer.render(
            template,
            {
                key: str(value)
                for key, value in values.items()
            },
        )

        raw = self._provider.generate(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return parser.parse(
            raw,
        )