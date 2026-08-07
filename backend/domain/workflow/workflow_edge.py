from __future__ import annotations

from pydantic import BaseModel


class WorkflowEdge(BaseModel):
    """
    Directed dependency between two workflow nodes.
    """

    from_node: str

    to_node: str