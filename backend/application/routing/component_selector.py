from __future__ import annotations

from backend.application.routing.intent_result import (
    IntentResult,
)
from backend.application.routing.routing_result import (
    RoutingResult,
)


class ComponentSelector:
    """
    Maps an IntentResult to a RoutingResult.

    This class contains the application's routing policy,
    translating learner intents into candidate components.
    """

    _INTENT_MAPPING: dict[str, list[str]] = {
        "explain": [
            "mentor",
        ],
        "summarize": [
            "mentor",
        ],
        "compare": [
            "research",
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

        return RoutingResult(
            intent=intent.intent,
            confidence=intent.confidence,
            candidate_components=self._INTENT_MAPPING.get(
                intent.intent,
                [],
            ).copy(),
            metadata=intent.metadata.copy(),
        )