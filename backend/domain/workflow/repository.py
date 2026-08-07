from __future__ import annotations

from abc import ABC, abstractmethod

from backend.domain.workflow.workflow import Workflow


class WorkflowRepository(ABC):
    """
    Domain repository for Workflow Aggregate.

    This interface belongs to the Domain Layer.

    Infrastructure implementations (SQLite, PostgreSQL,
    MongoDB, etc.) must implement this contract.
    """

    @abstractmethod
    def add(
        self,
        workflow: Workflow,
    ) -> None:
        """
        Persist a new workflow.
        """
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        workflow_id: str,
    ) -> Workflow | None:
        """
        Retrieve a workflow by id.
        """
        raise NotImplementedError

    @abstractmethod
    def list(
        self,
    ) -> list[Workflow]:
        """
        Retrieve all workflows.
        """
        raise NotImplementedError

    @abstractmethod
    def remove(
        self,
        workflow_id: str,
    ) -> None:
        """
        Remove a workflow.
        """
        raise NotImplementedError