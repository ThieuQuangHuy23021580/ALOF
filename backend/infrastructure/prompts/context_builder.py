from __future__ import annotations

from backend.core.component_context import ComponentContext


class ContextBuilder:
    """
    Build the prompt messages for a single Component execution.

    ContextBuilder is responsible only for transforming
    ComponentContext into LLM messages.

    Dependency resolution is handled by Runtime.
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

        # ======================================================
        # Workflow Status
        # ======================================================

        messages.append(
            {
                "role": "system",
                "content": f"""
================ CURRENT WORKFLOW ================

Current Component

{node.component_id}

Objective

{node.objective}

Expected Output

{node.expected_output}

==================================================
""".strip(),
            }
        )

        # ======================================================
        # Dependency Artifacts
        # ======================================================

        dependency_blocks: list[str] = []

        for node_id, artifact in context.inputs.items():

            dependency_blocks.append(
                f"""
Source Node

{node_id}

Title

{artifact.title}

Artifact Type

{artifact.type}

Summary

{artifact.summary}

Content

{artifact.content}
""".strip()
            )

        if dependency_blocks:

            messages.append(
                {
                    "role": "system",
                    "content": f"""
================ DEPENDENCY ARTIFACTS ================

The following artifacts were produced by
previous components and are available as inputs.

Use them when relevant.

Do not regenerate information that is
already provided by these artifacts.

------------------------------------------------------

{chr(10).join(dependency_blocks)}

======================================================
""".strip(),
                }
            )

        return messages

