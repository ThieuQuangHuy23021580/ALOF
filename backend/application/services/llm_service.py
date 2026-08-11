from __future__ import annotations

from backend.infrastructure.providers import (
    ProviderFactory,
    LLMProvider,
)


class LLMService:
    """
    Application service for LLM access.
    """

    def __init__(
        self,
        provider: LLMProvider | None = None,
    ) -> None:

        self._provider = (
            provider
            if provider is not None
            else ProviderFactory.create()
        )


    @property
    def provider(
        self,
    ) -> LLMProvider:

        return self._provider


    def generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:

        return self._provider.generate(
            messages,
        )


    def set_provider(
        self,
        provider: LLMProvider,
    ) -> None:

        self._provider = provider