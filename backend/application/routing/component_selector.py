from __future__ import annotations

from backend.application.routing.intent_result import (
    IntentResult,
)
from backend.application.routing.routing_result import (
    RoutingResult,
)


class ComponentSelector:
    """
    Maps recognized learner intents to candidate components.
    """

    _INTENT_MAPPING: dict[str, list[str]] = {
        "explain": [
            "mentor",
        ],
        "summarize": [
            "mentor",
        ],
        "compare": [
            "mentor",
        ],
        "roadmap": [
            "planner",
        ],
        "quiz": [
            "quiz",
        ],
        "flashcard": [
            "flashcard",
        ],
        "unknown": [],
    }

    def select(
        self,
        intent: IntentResult,
    ) -> RoutingResult:

        candidate_components: list[str] = []

        confidences: list[float] = []

        recognized_intents: list[str] = []

        for item in intent.intents:

            recognized_intents.append(
                item.intent,
            )

            confidences.append(
                item.confidence,
            )

            for component in self._INTENT_MAPPING.get(
                item.intent,
                [],
            ):
                if component not in candidate_components:
                    candidate_components.append(
                        component,
                    )

        confidence = (
            min(confidences)
            if confidences
            else 0.0
        )

        return RoutingResult(
            intents=recognized_intents,
            confidence=confidence,
            candidate_components=candidate_components,
            metadata=intent.metadata.copy(),
        )