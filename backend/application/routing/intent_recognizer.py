from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from .intent_result import IntentResult


class IntentRecognizer(ABC):
    """
    Recognizes the learner's intent.

    Implementations may use LLMs, embeddings,
    classifiers or rule-based approaches.
    """

    @abstractmethod
    def recognize(
        self,
        message: str,
    ) -> IntentResult:
        """
        Recognize the learner intent.
        """
        raise NotImplementedError