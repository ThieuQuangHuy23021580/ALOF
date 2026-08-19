from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BenchmarkScenario(BaseModel):
    """
    Defines one benchmark scenario for ALOF.

    A scenario contains benchmark data and execution
    requirements, but does not execute anything itself.
    """

    id: str

    name: str

    user_request: str

    component_ids: list[str] = Field(
        default_factory=list,
    )

    expected_output: Any

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    agent_count: int = 1

    agent_inputs: dict[int, Any] = Field(
        default_factory=dict,
    )

    def get_agent_input(
        self,
        agent_id: int,
    ) -> Any:
        """
        Return private input belonging to one agent.
        """

        if agent_id not in self.agent_inputs:
            raise KeyError(
                f"No input found for agent {agent_id}."
            )

        return self.agent_inputs[agent_id]

    @property
    def paradigm(self) -> str | None:
        """
        Return benchmark paradigm if provided.
        """

        value = self.metadata.get(
            "paradigm",
        )

        if value is None:
            return None

        return str(value)

    @property
    def protocol(self) -> str | None:
        """
        Return communication protocol if provided.
        """

        value = self.metadata.get(
            "protocol",
        )

        if value is None:
            return None

        return str(value)

    @property
    def topology(self) -> str | None:
        """
        Return optimal topology if provided.
        """

        value = self.metadata.get(
            "optimal_topology",
        )

        if value is None:
            return None

        return str(value)