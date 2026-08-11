from __future__ import annotations

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from openai import RateLimitError

from backend.infrastructure.providers.groq_provider import (
    GroqProvider,
)


class FakeResponse:

    output_text = "Hello from Groq"


def test_groq_provider_initialization():

    with patch(
        "backend.infrastructure.providers.groq_provider.OpenAI"
    ) as mock_openai:

        provider = GroqProvider()

        mock_openai.assert_called_once()

        assert provider.model is not None

        assert provider.client is (
            mock_openai.return_value
        )


def test_groq_provider_generate():

    with patch(
        "backend.infrastructure.providers.groq_provider.OpenAI"
    ) as mock_openai:

        client = mock_openai.return_value

        client.responses.create.return_value = (
            FakeResponse()
        )

        provider = GroqProvider()

        messages = [
            {
                "role": "user",
                "content": "Hello",
            }
        ]

        result = provider.generate(
            messages,
        )

        assert result == "Hello from Groq"

        client.responses.create.assert_called_once()


def test_groq_provider_generate_passes_messages():

    with patch(
        "backend.infrastructure.providers.groq_provider.OpenAI"
    ) as mock_openai:

        client = mock_openai.return_value

        client.responses.create.return_value = (
            FakeResponse()
        )

        provider = GroqProvider()

        messages = [
            {
                "role": "system",
                "content": "You are helpful.",
            },
            {
                "role": "user",
                "content": "Explain Python.",
            },
        ]

        provider.generate(
            messages,
        )

        call = (
            client.responses.create.call_args
        )

        assert call.kwargs["model"] == (
            provider.model
        )

        assert call.kwargs["input"] == (
            messages
        )


def test_groq_provider_retries_on_rate_limit():

    with patch(
        "backend.infrastructure.providers.groq_provider.OpenAI"
    ) as mock_openai, patch(
        "backend.infrastructure.providers.groq_provider.time.sleep"
    ) as mock_sleep:

        client = mock_openai.return_value

        client.responses.create.side_effect = [
            RateLimitError(
                "rate limit",
                response=MagicMock(),
                body=None,
            ),
            FakeResponse(),
        ]

        provider = GroqProvider()

        result = provider.generate(
            [
                {
                    "role": "user",
                    "content": "Hello",
                }
            ],
        )

        assert result == "Hello from Groq"

        assert (
            client.responses.create.call_count
            == 2
        )

        mock_sleep.assert_called_once_with(
            1.0,
        )


def test_groq_provider_uses_exponential_backoff():

    with patch(
        "backend.infrastructure.providers.groq_provider.OpenAI"
    ) as mock_openai, patch(
        "backend.infrastructure.providers.groq_provider.time.sleep"
    ) as mock_sleep:

        client = mock_openai.return_value

        client.responses.create.side_effect = [
            RateLimitError(
                "rate limit",
                response=MagicMock(),
                body=None,
            ),
            RateLimitError(
                "rate limit",
                response=MagicMock(),
                body=None,
            ),
            FakeResponse(),
        ]

        provider = GroqProvider()

        result = provider.generate(
            [
                {
                    "role": "user",
                    "content": "Hello",
                }
            ],
        )

        assert result == "Hello from Groq"

        assert (
            client.responses.create.call_count
            == 3
        )

        assert mock_sleep.call_count == 2

        assert mock_sleep.call_args_list[0].args == (
            1.0,
        )

        assert mock_sleep.call_args_list[1].args == (
            2.0,
        )


def test_groq_provider_raises_after_max_retries():

    with patch(
        "backend.infrastructure.providers.groq_provider.OpenAI"
    ) as mock_openai, patch(
        "backend.infrastructure.providers.groq_provider.time.sleep"
    ) as mock_sleep:

        client = mock_openai.return_value

        error = RateLimitError(
            "rate limit",
            response=MagicMock(),
            body=None,
        )

        client.responses.create.side_effect = [
            error,
            error,
            error,
        ]

        provider = GroqProvider()

        with pytest.raises(
            RateLimitError,
        ):
            provider.generate(
                [
                    {
                        "role": "user",
                        "content": "Hello",
                    }
                ],
            )

        assert (
            client.responses.create.call_count
            == 3
        )

        assert mock_sleep.call_count == 2