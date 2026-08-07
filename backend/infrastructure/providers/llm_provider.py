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