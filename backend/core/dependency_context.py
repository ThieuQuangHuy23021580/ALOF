from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class DependencyContext(BaseModel):
    """
    Runtime dependencies available to a Component.

    DependencyContext provides a controlled boundary between
    the runtime and executable Components.

    Components can retrieve runtime services without knowing
    how those services were created or injected.
    """

    dependencies: dict[str, Any] = Field(
        default_factory=dict,
    )

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.dependencies.get(
            key,
            default,
        )

    def has(
        self,
        key: str,
    ) -> bool:

        return key in self.dependencies

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.dependencies[key] = value

    def keys(
        self,
    ) -> list[str]:

        return list(
            self.dependencies.keys(),
        )