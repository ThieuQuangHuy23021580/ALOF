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
    - Use adaptive learning decisions to guide the plan.
    - Determine execution order and dependencies.
    - Determine adaptive teaching information for plan steps.
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
        learning_state = request.learning_state

        adaptive_learning = (
            request.adaptive_learning
        )

        historical_evidence = (
            adaptive_learning.evidence
        )

        knowledge_diagnosis = (
            adaptive_learning.diagnosis
        )

        adaptive_teaching_action = (
            adaptive_learning.teaching_action
        )

        candidate_components = json.dumps(
            routing.candidate_components,
            ensure_ascii=False,
        )

        learner_state = json.dumps(
            learning_state.model_dump(),
            ensure_ascii=False,
        )

        historical_evidence_data = json.dumps(
            historical_evidence.model_dump(),
            ensure_ascii=False,
        )

        knowledge_diagnosis_data = json.dumps(
            knowledge_diagnosis.model_dump(),
            ensure_ascii=False,
        )

        adaptive_action_data = json.dumps(
            adaptive_teaching_action.model_dump(),
            ensure_ascii=False,
        )

        return f"""
CURRENT TASK
{request.message}

ROUTING RESULT
Intents:
{routing.intents}

Routing Confidence:
{routing.confidence}

Candidate Components:
{candidate_components}

LEARNING STATE
{learner_state}

HISTORICAL EVIDENCE
{historical_evidence_data}

KNOWLEDGE DIAGNOSIS
{knowledge_diagnosis_data}

ADAPTIVE TEACHING ACTION
{adaptive_action_data}

PLANNING REQUIREMENTS

Create an execution plan for CURRENT TASK.

The plan must:

1. Use only appropriate candidate components.
2. Respect the current learner state.
3. Use Historical Evidence as supporting context.
4. Follow Knowledge Diagnosis.
5. Follow Adaptive Teaching Action.
6. Prioritize focus_concepts from Adaptive Teaching Action.
7. Respect the selected difficulty.
8. Define clear component responsibilities.
9. Define execution order and dependencies.
10. Produce executable logical steps.

Each plan step should explicitly preserve the
adaptive teaching decision when applicable:

- action
- strategy
- difficulty
- focus_concepts

Do not put these adaptive teaching fields only
inside metadata.

Do not execute any component.
Do not explain the knowledge.
Do not perform diagnosis.

Only create the execution plan.

Return only the JSON object required by the
Planner output contract.
""".strip()