from __future__ import annotations

import re

from backend.application.services.llm_service import (
    LLMService,
)
from backend.core.component import Component
from backend.core.component_context import ComponentContext
from backend.core.component_result import ComponentResult


class WordFrequencyLLMComponent(Component):
    """
    LLM-powered local computation for SILO-BENCH I-02.

    Each agent receives only its private shard and asks
    the LLM to count occurrences of the target word.

    The component performs local computation only.
    Global coordination is handled by the benchmark runner.
    """

    component_id = (
        "benchmark.word_frequency_llm"
    )

    name = "SILO-BENCH Word Frequency LLM Agent"

    description = (
        "Uses an LLM to count occurrences of a target "
        "word inside one private agent shard."
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
                "WordFrequencyLLMComponent requires "
                "an LLMService dependency."
            )

        agent_id = context.get_input(
            "agent_id",
        )

        input_shard = context.get_input(
            "input_shard",
        )

        target_word = context.get_input(
            "target_word",
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

        if not isinstance(
            target_word,
            str,
        ):
            raise ValueError(
                "target_word must be a string."
            )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an agent participating in "
                    "a distributed word-frequency task. "
                    "You must count how many times the "
                    "target word appears in your private "
                    "shard. Return only the integer count."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Agent ID: {agent_id}\n"
                    f"Target word: {target_word}\n"
                    f"Private shard: {input_shard}\n\n"
                    f"Count the exact occurrences of "
                    f'"{target_word}" in this shard. '
                    "Return only one integer."
                ),
            },
        ]

        response = llm.generate(
            messages,
            stage="benchmark",
            component=self.component_id,
        )

        local_count = self._parse_integer(
            response,
        )

        return ComponentResult(
            artifact={
                "agent_id": agent_id,
                "target_word": target_word,
                "local_count": local_count,
                "raw_response": response,
            },
            metadata={
                "agent_id": agent_id,
                "target_word": target_word,
                "local_count": local_count,
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