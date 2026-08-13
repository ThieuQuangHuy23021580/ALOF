from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class IntentItem(BaseModel):
    """
    Represents one recognized learner intent.
    """

    intent: str

    confidence: float = 1.0


class IntentResult(BaseModel):
    """
    Result produced by an IntentRecognizer.

    A learner request may contain multiple intents.
    """

    intents: list[IntentItem] = Field(
        default_factory=list,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    def add_intent(
        self,
        intent: IntentItem,
    ) -> None:

        if intent.intent not in {
            item.intent
            for item in self.intents
        }:
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