from __future__ import annotations

import json
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from backend.core.parser import Parser

T = TypeVar(
    "T",
    bound=BaseModel,
)


class JsonParser(Parser[T]):
    """
    Generic JSON parser for Pydantic models.
    """

    def __init__(
        self,
        model_type: type[T],
    ) -> None:

        self._model_type = model_type

    def parse(
        self,
        raw: str,
    ) -> T:

        try:

            data = json.loads(
                raw,
            )

        except json.JSONDecodeError as exc:

            raise ValueError(
                "Invalid JSON response.",
            ) from exc

        try:

            return self._model_type.model_validate(
                data,
            )

        except ValidationError as exc:

            raise ValueError(
                "Invalid response schema.",
            ) from exc