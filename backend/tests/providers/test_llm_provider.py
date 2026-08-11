from __future__ import annotations

import pytest

from backend.infrastructure.providers.llm_provider import (
    LLMProvider,
)


class FakeProvider(LLMProvider):

    def generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:

        return "fake response"


def test_llm_provider_is_abstract():

    with pytest.raises(
        TypeError,
    ):
        LLMProvider()


def test_fake_provider_implements_provider():

    provider = FakeProvider()

    result = provider.generate(
        [
            {
                "role": "user",
                "content": "Hello",
            }
        ],
    )

    assert result == "fake response"