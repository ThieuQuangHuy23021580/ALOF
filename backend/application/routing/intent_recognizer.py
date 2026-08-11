from __future__ import annotations

from abc import ABC, abstractmethod

from .intent_result import IntentResult


class IntentRecognizer(ABC):
    """
    Recognizes the learner's intent from an input message.

    Implementations may use an LLM, rules, embeddings,
    classifiers or hybrid approaches.
    """


    @abstractmethod
    def recognize(
        self,
        message: str,
    ) -> IntentResult:
        """
        Returns an IntentResult.
        """
        raise NotImplementedError