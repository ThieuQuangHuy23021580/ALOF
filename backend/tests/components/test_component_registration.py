from __future__ import annotations

from backend.components.mentor.mentor_component import (
    MentorComponent,
)
from backend.core.component_registry import (
    ComponentRegistry,
)


def test_mentor_component_registration():

    ComponentRegistry.clear()

    ComponentRegistry.register(
        MentorComponent,
    )

    assert ComponentRegistry.exists(
        "mentor",
    )

    assert "mentor" in ComponentRegistry.ids()

    component = ComponentRegistry.create(
        "mentor",
    )

    assert isinstance(
        component,
        MentorComponent,
    )