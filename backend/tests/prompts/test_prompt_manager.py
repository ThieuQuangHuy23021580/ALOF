
from __future__ import annotations

import pytest

from backend.infrastructure.prompts.manager import (
    PromptManager,
)


def test_prompt_manager_loads_registered_prompt():

    prompt = PromptManager.get(
        "mentor",
    )

    assert isinstance(
        prompt,
        str,
    )

    assert prompt.strip()


def test_prompt_manager_returns_mentor_prompt():

    prompt = PromptManager.get(
        "mentor",
    )

    assert isinstance(
        prompt,
        str,
    )

    assert len(
        prompt.strip(),
    ) > 0


def test_prompt_manager_rejects_unknown_prompt():

    with pytest.raises(
        FileNotFoundError,
    ):
        PromptManager.get(
            "unknown_component",
        )