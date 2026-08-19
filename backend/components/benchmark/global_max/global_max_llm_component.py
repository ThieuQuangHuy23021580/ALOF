from __future__ import annotations

import re

from backend.application.services.llm_service import (
    LLMService,
)
from backend.core.component import Component
from backend.core.component_context import ComponentContext
from backend.core.component_result import ComponentResult


class GlobalMaxLLMComponent(Component):
    """
    LLM-powered local computation for SILO-BENCH I-01.

    The component gives an agent only its private input shard
    and asks the LLM to compute the local maximum.

    The component does not perform global coordination.
    """

    component_id = "benchmark.global_max_llm"

    name = "SILO-BENCH Global Max LLM Agent"

    description = (
        "Uses an LLM to compute the maximum value "
        "from one private agent shard."
    )

    version = "1.0.0"

    def execute(
        self,
        context: ComponentContext,
    ) -> ComponentResult:

        llm = context.get_dependency(
            "llm",
        )

        if not isinstance(
            llm,
            LLMService,
        ):
            raise TypeError(
                "GlobalMaxLLMComponent requires "
                "an LLMService dependency."
            )

        agent_id = context.get_input(
            "agent_id",
        )

        input_shard = context.get_input(
            "input_shard",
        )

        if agent_id is None:
            raise ValueError(
                "agent_id is required."
            )

        if not isinstance(
            input_shard,
            list,
        ):
            raise ValueError(
                "input_shard must be a list."
            )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an agent participating in "
                    "a distributed maximum-finding task. "
                    "You must compute the maximum value "
                    "of your private shard. "
                    "Return only the integer maximum value."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Agent ID: {agent_id}\n"
                    f"Private shard: {input_shard}\n\n"
                    "Find the maximum value in this shard. "
                    "Return only one integer."
                ),
            },
        ]

        response = llm.generate(
            messages,
            stage="benchmark",
            component=self.component_id,
        )

        local_max = self._parse_integer(
            response,
        )

        return ComponentResult(
            artifact={
                "agent_id": agent_id,
                "local_max": local_max,
                "raw_response": response,
            },
            metadata={
                "agent_id": agent_id,
                "local_max": local_max,
                "raw_response": response,
            },
        )

    @staticmethod
    def _parse_integer(
        response: str,
    ) -> int:

        match = re.search(
            r"-?\d+",
            response,
        )

        if match is None:
            raise ValueError(
                "LLM response does not contain "
                "an integer."
            )

        return int(
            match.group(),
        )