from __future__ import annotations

from backend.application.services.llm_service import (
    LLMService,
)
from backend.components.mentor.mentor_component import (
    MentorComponent,
)
from backend.core.component_registry import (
    ComponentRegistry,
)


class FakeLLMProvider:

    def generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:

        return "fake"


def test_component_registry_injects_dependencies():

    ComponentRegistry.clear()

    ComponentRegistry.register(
        MentorComponent,
    )

    llm = LLMService(
        provider=FakeLLMProvider(),
    )

    component = ComponentRegistry.create(
        "mentor",
        llm=llm,
    )

    assert isinstance(
        component,
        MentorComponent,
    )

    assert component._llm is llm