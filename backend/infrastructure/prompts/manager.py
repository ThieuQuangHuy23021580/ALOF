from __future__ import annotations

from pathlib import Path

from .loader import PromptLoader


class PromptManager:
    """
    Prompt cache for the whole application.
    """

    _cache: dict[str, str] = {}

    @classmethod
    def get(
        cls,
        name: str,
    ) -> str:

        if name not in cls._cache:

            filename = f"{name}.md"

            cls._cache[
                name
            ] = PromptLoader.load(
                filename,
            )

        return cls._cache[
            name
        ]

    @classmethod
    def exists(
        cls,
        name: str,
    ) -> bool:

        return (
            Path(__file__).parent /
            f"{name}.md"
        ).exists()

    @classmethod
    def available_prompts(
        cls,
    ) -> list[str]:

        return sorted(
            file.stem
            for file in Path(__file__).parent.glob(
                "*.md",
            )
        )

    @classmethod
    def clear_cache(
        cls,
    ) -> None:

        cls._cache.clear()