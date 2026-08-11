from __future__ import annotations

import json
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from backend.core.parser import Parser


T = TypeVar(
    "T",
    bound=BaseModel,
)


class JsonParser(Parser[T]):
    """
    Generic JSON parser for Pydantic models.

    Accepts:
    - Raw JSON string.
    - Already-decoded JSON object.

    The parser is responsible only for converting
    JSON data into the target Pydantic model.
    """

    def __init__(
        self,
        model_type: type[T],
    ) -> None:

        self._model_type = model_type

    def parse(
        self,
        raw: str | dict[str, Any],
    ) -> T:

        # ======================================================
        # Decode JSON
        # ======================================================

        if isinstance(
            raw,
            str,
        ):

            try:

                data = json.loads(
                    raw,
                )

            except json.JSONDecodeError as exc:

                raise ValueError(
                    "Invalid JSON response.",
                ) from exc

        elif isinstance(
            raw,
            dict,
        ):

            data = raw

        else:

            raise TypeError(
                "JsonParser expects a JSON string "
                "or dictionary.",
            )

        # ======================================================
        # Validate Schema
        # ======================================================

        try:

            return self._model_type.model_validate(
                data,
            )

        except ValidationError as exc:

            raise ValueError(
                "Invalid response schema.",
            ) from exc