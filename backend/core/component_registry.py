from __future__ import annotations

from typing import Type

from .component import Component


class ComponentRegistry:
    """
    Global registry of executable Components.
    """

    _components: dict[str, Type[Component]] = {}

    @classmethod
    def register(
        cls,
        component: Type[Component],
    ) -> None:

        component_id = component.component_id

        if not component_id:
            raise ValueError(
                f"{component.__name__} has no component_id."
            )

        if component_id in cls._components:
            raise ValueError(
                f"Duplicate component_id '{component_id}'."
            )

        cls._components[
            component_id
        ] = component

    @classmethod
    def create(
        cls,
        component_id: str,
    ) -> Component:

        component = cls.get(
            component_id,
        )

        return component()

    @classmethod
    def get(
        cls,
        component_id: str,
    ) -> Type[Component]:

        if component_id not in cls._components:
            raise ValueError(
                f"Unknown component '{component_id}'."
            )

        return cls._components[
            component_id
        ]

    @classmethod
    def exists(
        cls,
        component_id: str,
    ) -> bool:

        return component_id in cls._components

    @classmethod
    def ids(
        cls,
    ) -> list[str]:

        return sorted(
            cls._components.keys(),
        )

    @classmethod
    def components(
        cls,
    ) -> list[Type[Component]]:

        return list(
            cls._components.values(),
        )

    @classmethod
    def clear(
        cls,
    ) -> None:

        cls._components.clear()