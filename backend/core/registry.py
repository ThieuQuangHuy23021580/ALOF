from __future__ import annotations

from typing import Dict, Generic, Iterable, TypeVar

from backend.core.contracts import Registrable
from backend.core.exceptions import ComponentAlreadyRegisteredError, RegistryLookupError

T = TypeVar("T", bound=Registrable)


class Registry(Generic[T]):
    """
    Generic registry for framework objects.

    Registry is responsible only for object registration
    and lookup. It does not perform routing or execution.
    """

    def __init__(self) -> None:
        self._items: Dict[str, T] = {}

    def register(
        self,
        item: T,
    ) -> None:
        if item.component_id in self._items:
            raise ComponentAlreadyRegisteredError(
                f"'{item.component_id}' is already registered."
            )

        self._items[item.component_id] = item

    def unregister(
        self,
        component_id: str,
    ) -> None:
        self._items.pop(
            component_id,
            None,
        )

    def exists(
        self,
        component_id: str,
    ) -> bool:
        return component_id in self._items

    def get(
        self,
        component_id: str,
    ) -> T:
        try:
            return self._items[component_id]
        except KeyError:
            raise RegistryLookupError(
                f"Component '{component_id}' is not registered."
            )

    def all(
        self,
    ) -> list[T]:
        return list(
            self._items.values()
        )

    def ids(
        self,
    ) -> list[str]:
        return sorted(
            self._items.keys()
        )

    def values(
        self,
    ) -> Iterable[T]:
        return self._items.values()

    def clear(
        self,
    ) -> None:
        self._items.clear()

    def __contains__(
        self,
        component_id: str,
    ) -> bool:
        return component_id in self._items

    def __len__(
        self,
    ) -> int:
        return len(
            self._items
        )