from __future__ import annotations

import json
from collections import Counter
from typing import Any

from backend.application.services.llm_service import (
    LLMService,
)
from backend.core.component import Component
from backend.core.component_context import ComponentContext
from backend.core.component_result import ComponentResult


class DistributedVoteLLMComponent(Component):
    """
    LLM-powered local vote counting for SILO-BENCH I-03.

    Each agent receives only its private shard and computes
    a local histogram of candidate votes.
    """

    component_id = (
        "benchmark.distributed_vote_llm"
    )

    name = "SILO-BENCH Distributed Vote LLM Agent"

    description = (
        "Uses an LLM to count candidate votes "
        "inside one private agent shard."
    )

    version = "1.0.0"

    def execute(
        self,
        context: ComponentContext,
    ) -> ComponentResult:

        llm = context.get_dependency("llm")

        if not isinstance(llm, LLMService):
            raise TypeError(
                "DistributedVoteLLMComponent requires "
                "an LLMService dependency."
            )

        agent_id = context.get_input("agent_id")
        input_shard = context.get_input("input_shard")

        if agent_id is None:
            raise ValueError(
                "agent_id is required."
            )

        if not isinstance(input_shard, list):
            raise ValueError(
                "input_shard must be a list."
            )

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an agent participating in "
                    "a distributed voting task. "
                    "You have access only to your private "
                    "data shard. Count how many votes each "
                    "candidate receives in this shard. "
                    "Return only a valid JSON object mapping "
                    "candidate names to integer vote counts. "
                    "Do not determine the global winner."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Agent ID: {agent_id}\n"
                    f"Private shard: {input_shard}\n\n"
                    "Count every candidate in this shard. "
                    "Return only JSON."
                ),
            },
        ]

        response = llm.generate(
            messages,
            stage="benchmark",
            component=self.component_id,
        )

        local_vote_counts = self._parse_counts(
            response,
        )

        return ComponentResult(
            artifact={
                "agent_id": agent_id,
                "local_vote_counts": local_vote_counts,
                "raw_response": response,
            },
            metadata={
                "agent_id": agent_id,
                "local_vote_counts": local_vote_counts,
                "raw_response": response,
            },
        )

    @staticmethod
    def _parse_counts(
        response: str,
    ) -> dict[str, int]:

        text = response.strip()

        if text.startswith("```"):
            lines = text.splitlines()

            if lines:
                lines = lines[1:]

            if (
                lines
                and lines[-1].strip() == "```"
            ):
                lines = lines[:-1]

            text = "\n".join(lines).strip()

        try:
            data: Any = json.loads(text)

        except json.JSONDecodeError as exc:
            raise ValueError(
                "LLM response does not contain "
                "valid JSON vote counts."
            ) from exc

        if not isinstance(data, dict):
            raise ValueError(
                "LLM response must be a JSON object."
            )

        counts: dict[str, int] = {}

        for candidate, count in data.items():

            if not isinstance(candidate, str):
                raise ValueError(
                    "Candidate names must be strings."
                )

            if (
                isinstance(count, bool)
                or not isinstance(count, int)
            ):
                raise ValueError(
                    "Vote counts must be integers."
                )

            if count < 0:
                raise ValueError(
                    "Vote counts cannot be negative."
                )

            counts[candidate] = count

        if not counts:
            raise ValueError(
                "Vote counts cannot be empty."
            )

        return counts


class DistributedVoteAggregatorComponent(Component):
    """
    Deterministically aggregates local vote histograms
    and determines the global winner.
    """

    component_id = (
        "benchmark.distributed_vote_aggregator"
    )

    name = "SILO-BENCH Distributed Vote Aggregator"

    description = (
        "Aggregates local vote histograms and "
        "determines the global winning candidate."
    )

    version = "1.0.0"

    def execute(
        self,
        context: ComponentContext,
    ) -> ComponentResult:

        local_vote_counts = context.get_input(
            "local_vote_counts",
        )

        if not isinstance(
            local_vote_counts,
            list,
        ):
            raise ValueError(
                "local_vote_counts must be a list."
            )

        if not local_vote_counts:
            raise ValueError(
                "local_vote_counts cannot be empty."
            )

        global_counts: Counter[str] = Counter()

        for counts in local_vote_counts:

            if not isinstance(counts, dict):
                raise ValueError(
                    "Each local vote count must be a dict."
                )

            for candidate, count in counts.items():

                if not isinstance(
                    candidate,
                    str,
                ):
                    raise ValueError(
                        "Candidate names must be strings."
                    )

                if (
                    isinstance(count, bool)
                    or not isinstance(count, int)
                ):
                    raise ValueError(
                        "Vote counts must be integers."
                    )

                if count < 0:
                    raise ValueError(
                        "Vote counts cannot be negative."
                    )

                global_counts[candidate] += count

        if not global_counts:
            raise ValueError(
                "Global vote counts cannot be empty."
            )

        winner = max(
            global_counts,
            key=lambda candidate: (
                global_counts[candidate],
                candidate,
            ),
        )

        return ComponentResult(
            artifact={
                "global_vote_counts": dict(
                    global_counts,
                ),
                "winner": winner,
            },
            metadata={
                "global_vote_counts": dict(
                    global_counts,
                ),
                "winner": winner,
            },
        )