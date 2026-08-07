from __future__ import annotations

from pathlib import Path


class PromptLoader:
    """
    Load prompt files from infrastructure/prompts.
    """

    PROMPT_DIR = Path(__file__).parent

    @classmethod
    def load(
        cls,
        filename: str,
    ) -> str:

        path = cls.PROMPT_DIR / filename

        if not path.exists():
            raise FileNotFoundError(
                f"Prompt not found: {path}"
            )

        return path.read_text(
            encoding="utf-8",
        )