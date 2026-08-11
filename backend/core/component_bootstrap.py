from __future__ import annotations

from backend.components.mentor.mentor_component import (
    MentorComponent,
)
from backend.core.component_registry import ComponentRegistry


def register_components() -> None:
    """
    Register all application components.

    This function is idempotent and safe to call
    during application startup.
    """

    registrations = [
        MentorComponent,
    ]

    for component in registrations:

        if ComponentRegistry.exists(
            component.component_id,
        ):
            continue

        ComponentRegistry.register(
            component,
        )