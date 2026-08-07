from __future__ import annotations

from backend.providers import ProviderFactory
from backend.providers.base_provider import BaseProvider


class LLMService:
    """
    Thin service responsible for communicating with the configured LLM provider.

    Responsibilities
    ----------------
    - Hold the current provider.
    - Forward generation requests.
    - Allow provider replacement (testing, multi-provider, etc.).
    """

    def __init__(
        self,
        provider: BaseProvider | None = None,
    ) -> None:

        self._provider = (
            provider
            if provider is not None
            else ProviderFactory.create()
        )

    @property
    def provider(
        self,
    ) -> BaseProvider:

        return self._provider

    def generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:

        return self._provider.generate(
            messages=messages,
        )

    def set_provider(
        self,
        provider: BaseProvider,
    ) -> None:

        self._provider = provider