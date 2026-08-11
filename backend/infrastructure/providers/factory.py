from __future__ import annotations

from backend.infrastructure.providers.groq_provider import GroqProvider

from .llm_provider import LLMProvider


class ProviderFactory:
    """
    Creates configured LLM providers.
    """


    @staticmethod
    def create() -> LLMProvider:

        return GroqProvider()