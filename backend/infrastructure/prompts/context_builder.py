from __future__ import annotations

from backend.core.component_context import ComponentContext


class ContextBuilder:
    """
    Build compact LLM messages for a component execution.

    The builder intentionally keeps the runtime context small.
    Large learner-history payloads should not be duplicated here.
    """

    @staticmethod
    def build(
        context: ComponentContext,
        system_prompt: str,
    ) -> list[dict[str, str]]:

        messages: list[dict[str, str]] = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]

        node = context.node
        learning_state = context.runtime.learning_state

        # ======================================================
        # Workflow
        # ======================================================

        messages.append(
            {
                "role": "system",
                "content": (
                    "CURRENT TASK\n\n"
                    f"Component: {node.component_id}\n"
                    f"Objective: {node.objective}\n"
                    f"Expected Output: {node.expected_output}"
                ),
            }
        )

        # ======================================================
        # Learner State
        # ======================================================

        messages.append(
            {
                "role": "system",
                "content": (
                    "LEARNER STATE\n\n"
                    f"Learner ID: {learning_state.learner_id}\n"
                    f"Current Knowledge: {learning_state.current_knowledge}\n"
                    f"Progress: {learning_state.progress}"
                ),
            }
        )

        # ======================================================
        # Dependency Artifacts
        # ======================================================

        for node_id, artifact in context.inputs.items():

            messages.append(
                {
                    "role": "system",
                    "content": (
                        "TASK INPUT\n\n"
                        f"Source: {node_id}\n"
                        f"Type: {artifact.type}\n"
                        f"Title: {artifact.title}\n\n"
                        f"{artifact.content}"
                    ),
                }
            )

        return messages