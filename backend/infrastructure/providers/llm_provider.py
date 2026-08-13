from __future__ import annotations

from abc import ABC
from abc import abstractmethod


class LLMProvider(ABC):
    """
    Contract for Large Language Model providers.

    Infrastructure implementations (Groq, Gemini,
    OpenAI, Ollama, etc.) must implement this interface.
    """

    @abstractmethod
    def generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:
        """
        Generate a completion from a chat conversation.
        """
        raise NotImplementedError

    # ======================================================
    # Usage metrics
    # ======================================================

    @property
    @abstractmethod
    def last_input_tokens(
        self,
    ) -> int:
        """
        Return input token usage from the most recent call.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def last_output_tokens(
        self,
    ) -> int:
        """
        Return output token usage from the most recent call.
        """
        raise NotImplementedError

    @property
    def last_total_tokens(
        self,
    ) -> int:
        """
        Return total token usage from the most recent call.
        """

        return (
            self.last_input_tokens
            + self.last_output_tokens
        )