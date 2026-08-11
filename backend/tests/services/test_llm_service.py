
from __future__ import annotations

from unittest.mock import patch

from backend.application.services.llm_service import (
    LLMService,
)
from backend.infrastructure.providers import (
    LLMProvider,
)
from backend.infrastructure.providers.groq_provider import (
    GroqProvider,
)


class FakeLLMProvider(LLMProvider):

    def __init__(
        self,
        response: str = "Fake response",
    ) -> None:

        self.response = response
        self.received_messages = None

    def generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:

        self.received_messages = messages

        return self.response


def test_llm_service_accepts_injected_provider():

    provider = FakeLLMProvider()

    service = LLMService(
        provider=provider,
    )

    assert service.provider is provider


def test_llm_service_generate_delegates_to_provider():

    provider = FakeLLMProvider(
        response="Hello from provider",
    )

    service = LLMService(
        provider=provider,
    )

    messages = [
        {
            "role": "user",
            "content": "Hello",
        }
    ]

    result = service.generate(
        messages,
    )

    assert result == "Hello from provider"

    assert provider.received_messages == (
        messages
    )


def test_llm_service_returns_provider_response():

    provider = FakeLLMProvider(
        response="Generated answer",
    )

    service = LLMService(
        provider=provider,
    )

    result = service.generate(
        [
            {
                "role": "user",
                "content": "Explain Python",
            }
        ],
    )

    assert result == "Generated answer"


def test_llm_service_set_provider():

    first_provider = FakeLLMProvider(
        response="First",
    )

    second_provider = FakeLLMProvider(
        response="Second",
    )

    service = LLMService(
        provider=first_provider,
    )

    assert service.generate(
        [
            {
                "role": "user",
                "content": "Hello",
            }
        ],
    ) == "First"

    service.set_provider(
        second_provider,
    )

    assert service.provider is second_provider

    assert service.generate(
        [
            {
                "role": "user",
                "content": "Hello",
            }
        ],
    ) == "Second"


def test_llm_service_default_provider():

    with patch(
        "backend.application.services.llm_service.ProviderFactory.create"
    ) as mock_create:

        provider = FakeLLMProvider()

        mock_create.return_value = provider

        service = LLMService()

        mock_create.assert_called_once()

        assert service.provider is provider


def test_llm_service_default_provider_can_be_groq():

    with patch(
        "backend.application.services.llm_service.ProviderFactory.create"
    ) as mock_create:

        provider = GroqProvider.__new__(
            GroqProvider,
        )

        mock_create.return_value = provider

        service = LLMService()

        assert service.provider is provider

