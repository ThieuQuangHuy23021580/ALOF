from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class IntentResult(BaseModel):
    """
    Result produced by an IntentRecognizer.
    """

    intent: str

    confidence: float = 1.0

    metadata: dict[str, Any] = Field(
        default_factory=dict,
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