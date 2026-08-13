from __future__ import annotations

import json

from backend.application.planning.plan import Plan
from backend.application.planning.planner import Planner
from backend.application.planning.planning_request import (
    PlanningRequest,
)
from backend.application.services.llm_service import (
    LLMService,
)
from backend.core.json_parser import JsonParser
from backend.infrastructure.prompts.manager import (
    PromptManager,
)


class LLMSequentialPlanner(Planner):
    """
    LLM-based sequential planner.

    Responsibilities
    ----------------
    - Convert RoutingResult into a logical execution plan.
    - Use an LLM to determine component responsibilities.
    - Determine execution order and dependencies.
    - Never execute components.
    - Never build a Workflow.
    """

    PROMPT_NAME = "llm_sequential_planner"

    def __init__(
        self,
        llm: LLMService | None = None,
    ) -> None:

        self._llm = (
            llm
            if llm is not None
            else LLMService()
        )

        self._parser = JsonParser(
            Plan,
        )

        self._system_prompt = (
            PromptManager.get(
                self.PROMPT_NAME,
            )
        )

    def plan(
        self,
        request: PlanningRequest,
    ) -> Plan:

        prompt = self._build_prompt(
            request,
        )

        messages = [
            {
                "role": "system",
                "content": self._system_prompt,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ]

        raw = self._llm.generate(
            messages,
            stage="planning",
        )

        return self._parser.parse(
            raw,
        )

    def _build_prompt(
        self,
        request: PlanningRequest,
    ) -> str:

        routing = request.routing

        candidate_components = json.dumps(
            routing.candidate_components,
            ensure_ascii=False,
        )

        return f"""
Learner Message:
{request.message}

Intent:
{routing.intents}

Routing Confidence:
{routing.confidence}

Candidate Components:
{candidate_components}
""".strip()