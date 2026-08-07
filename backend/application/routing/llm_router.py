from __future__ import annotations

from backend.application.routing.component_selector import (
    ComponentSelector,
)
from backend.application.routing.intent_recognizer import (
    IntentRecognizer,
)
from backend.application.routing.llm_intent_recognizer import (
    LLMIntentRecognizer,
)
from backend.domain.student.student import Student

from .router import Router
from .routing_result import RoutingResult


class LLMRouter(Router):
    """
    Default Router implementation.

    Responsibilities
    ----------------
    - Recognize learner intent.
    - Select candidate components.
    - Produce a RoutingResult.

    It never performs planning or workflow creation.
    """

    def __init__(
        self,
        recognizer: IntentRecognizer | None = None,
        selector: ComponentSelector | None = None,
    ) -> None:

        self._recognizer = (
            recognizer
            if recognizer is not None
            else LLMIntentRecognizer()
        )

        self._selector = (
            selector
            if selector is not None
            else ComponentSelector()
        )

    def route(
        self,
        student: Student,
        message: str,
    ) -> RoutingResult:

        intent = self._recognizer.recognize(
            message,
        )

        result = self._selector.select(
            intent,
        )

        result.set_metadata(
            "student_id",
            student.id,
        )

        return result