from __future__ import annotations

import pytest

from backend.application.runtime.runtime_context import (
    RuntimeContext,
)
from backend.components.mentor.mentor_component import (
    MentorComponent,
)
from backend.core.component_context import (
    ComponentContext,
)
from backend.core.dependency_context import (
    DependencyContext,
)
from backend.domain.learning.learning_state import (
    LearningState,
)
from backend.domain.workflow.workflow import (
    Workflow,
)
from backend.domain.workflow.workflow_node import (
    WorkflowNode,
)
from backend.infrastructure.providers.groq_provider import (
    GroqProvider,
)
from backend.application.services.llm_service import (
    LLMService,
)


def test_mentor_real_llm_receives_learning_state():

    # ==========================================================
    # Real LLM Provider
    # ==========================================================

    provider = GroqProvider()

    # ==========================================================
    # Workflow
    # ==========================================================

    workflow = Workflow()

    node = WorkflowNode(
        id="mentor",
        component_id="mentor",
        objective=(
            "Explain REST and GraphQL "
            "for the learner."
        ),
        expected_output="Lesson",
    )

    workflow.add_node(
        node,
    )

    # ==========================================================
    # Learner State
    # ==========================================================

    learning_state = LearningState(
        learner_id="learner-1",
        current_knowledge={
            "rest": "intermediate",
            "graphql": "basic",
        },
        progress={
            "rest": 0.7,
            "graphql": 0.4,
        },
        metadata={
            "preferred_difficulty": "medium",
            "preferred_pace": "normal",
        },
    )

    # ==========================================================
    # Runtime Context
    # ==========================================================

    runtime = RuntimeContext(
        workflow=workflow,
        learning_state=learning_state,
    )

    # ==========================================================
    # Component Context
    # ==========================================================

    context = ComponentContext(
        runtime=runtime,
        node=node,
        dependencies=DependencyContext(
            dependencies={
                "llm": LLMService(
                    provider=provider,
                ),
            },
        ),
    )

    # ==========================================================
    # Execute Real LLM
    # ==========================================================

    component = MentorComponent()

    result = component.invoke(
        context,
    )

    # ==========================================================
    # Verify Artifact
    # ==========================================================

    assert result.artifact is not None

    assert result.artifact.title

    assert result.artifact.content

    assert result.artifact.summary

    # ==========================================================
    # Verify Learning Content
    # ==========================================================

    content = result.artifact.content.lower()

    assert "rest" in content

    assert "graphql" in content

    # ==========================================================
    # Verify Real LLM Usage
    # ==========================================================

    assert provider.last_total_tokens > 0