from __future__ import annotations

from pydantic import BaseModel, Field

from .workflow_edge import WorkflowEdge
from .workflow_node import WorkflowNode


class Workflow(BaseModel):
    """
    Executable workflow graph.

    The workflow is immutable during runtime.
    It describes execution order and dependencies
    between workflow nodes.
    """

    nodes: list[WorkflowNode] = Field(
        default_factory=list,
    )

    edges: list[WorkflowEdge] = Field(
        default_factory=list,
    )

    def add_node(
        self,
        node: WorkflowNode,
    ) -> None:

        self.nodes.append(
            node,
        )

    def add_edge(
        self,
        edge: WorkflowEdge,
    ) -> None:

        self.edges.append(
            edge,
        )

    def get_node(
        self,
        node_id: str,
    ) -> WorkflowNode | None:

        return next(
            (
                node
                for node in self.nodes
                if node.id == node_id
            ),
            None,
        )

    def start_nodes(
        self,
    ) -> list[WorkflowNode]:

        destinations = {
            edge.to_node
            for edge in self.edges
        }

        destinations.update(
            node.id
            for node in self.nodes
            for dependency in node.depends_on
            if dependency
        )

        return [
            node
            for node in self.nodes
            if node.id not in destinations
        ]

    def parents(
        self,
        node_id: str,
    ) -> list[WorkflowNode]:

        node = self.get_node(
            node_id,
        )

        if node is None:
            return []

        parent_ids = {
            edge.from_node
            for edge in self.edges
            if edge.to_node == node_id
        }

        parent_ids.update(
            node.depends_on,
        )

        return [
            parent
            for parent in self.nodes
            if parent.id in parent_ids
        ]

    def children(
        self,
        node_id: str,
    ) -> list[WorkflowNode]:

        child_ids = {
            edge.to_node
            for edge in self.edges
            if edge.from_node == node_id
        }

        child_ids.update(
            node.id
            for node in self.nodes
            if node_id in node.depends_on
        )

        return [
            node
            for node in self.nodes
            if node.id in child_ids
        ]

    def incoming_edges(
        self,
        node_id: str,
    ) -> list[WorkflowEdge]:

        return [
            edge
            for edge in self.edges
            if edge.to_node == node_id
        ]

    def outgoing_edges(
        self,
        node_id: str,
    ) -> list[WorkflowEdge]:

        return [
            edge
            for edge in self.edges
            if edge.from_node == node_id
        ]

    def total_nodes(
        self,
    ) -> int:

        return len(
            self.nodes,
        )

    def total_edges(
        self,
    ) -> int:

        return len(
            self.edges,
        )

    def is_empty(
        self,
    ) -> bool:

        return not self.nodes

    def contains(
        self,
        node_id: str,
    ) -> bool:

        return (
            self.get_node(
                node_id,
            )
            is not None
        )