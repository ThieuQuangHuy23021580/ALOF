from __future__ import annotations

from backend.infrastructure.providers.factory import (
    ProviderFactory,
)
from backend.infrastructure.providers.groq_provider import (
    GroqProvider,
)


def test_provider_factory_creates_groq_provider():

    provider = ProviderFactory.create()

    assert isinstance(
        provider,
        GroqProvider,
    )