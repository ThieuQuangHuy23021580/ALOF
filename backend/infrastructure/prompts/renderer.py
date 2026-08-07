from __future__ import annotations

from backend.infrastructure.prompts.loader import PromptLoader


class PromptRenderer:
    """
    Renders prompt templates by replacing placeholders.
    """

    def __init__(
        self,
        loader: PromptLoader,
    ) -> None:

        self._loader = loader

    def render(
        self,
        template: str,
        values: dict[str, str],
    ) -> str:

        prompt = self._loader.load(
            template,
        )

        for key, value in values.items():

            prompt = prompt.replace(
                "{{" + key + "}}",
                value,
            )

        return prompt