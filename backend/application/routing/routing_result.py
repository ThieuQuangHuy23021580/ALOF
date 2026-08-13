from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RoutingResult(BaseModel):
    """
    Output of the routing stage.

    RoutingResult captures the learner's intents
    and candidate components.
    """

    intents: list[str] = Field(
        default_factory=list,
    )

    candidate_components: list[str] = Field(
        default_factory=list,
    )

    confidence: float = 1.0

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    def add_component(
        self,
        component_id: str,
    ) -> None:

        if component_id not in self.candidate_components:
            self.candidate_components.append(
                component_id,
            )

    def add_intent(
        self,
        intent: str,
    ) -> None:

        if intent not in self.intents:
            self.intents.append(
                intent,
            )

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.metadata.get(
            key,
            default,
        )