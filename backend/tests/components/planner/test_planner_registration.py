from __future__ import annotations

from backend.components.planner.planner_component import (
    PlannerComponent,
)
from backend.core.component_registry import (
    ComponentRegistry,
)


def test_planner_component_registration():

    ComponentRegistry.clear()

    ComponentRegistry.register(
        PlannerComponent,
    )

    component = ComponentRegistry.create(
        "planner",
    )

    assert isinstance(
        component,
        PlannerComponent,
    )