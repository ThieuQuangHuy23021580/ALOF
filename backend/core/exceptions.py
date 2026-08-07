from __future__ import annotations


class ALOFError(Exception):
    """
    Base exception of the ALOF framework.
    """

    pass


# ==========================================================
# Component
# ==========================================================

class ComponentError(ALOFError):
    """Base component exception."""


class ComponentNotFoundError(ComponentError):
    """Component is not registered."""


class ComponentAlreadyRegisteredError(ComponentError):
    """Duplicate component registration."""


class ComponentExecutionError(ComponentError):
    """Component execution failed."""


# ==========================================================
# Workflow
# ==========================================================

class WorkflowError(ALOFError):
    """Base workflow exception."""


class InvalidWorkflowError(WorkflowError):
    """Workflow structure is invalid."""


class TaskDependencyError(WorkflowError):
    """Workflow dependency is invalid."""


class TaskExecutionError(WorkflowError):
    """Task execution failed."""


# ==========================================================
# Registry
# ==========================================================

class RegistryError(ALOFError):
    """Base registry exception."""


class RegistryLookupError(RegistryError):
    """Registry lookup failed."""


# ==========================================================
# Artifact
# ==========================================================

class ArtifactError(ALOFError):
    """Base artifact exception."""


class InvalidArtifactError(ArtifactError):
    """Artifact is invalid."""


# ==========================================================
# Runtime
# ==========================================================

class RuntimeError(ALOFError):
    """Base runtime exception."""


class ContextError(RuntimeError):
    """RuntimeContext is invalid."""


# ==========================================================
# Contract
# ==========================================================

class ContractError(ALOFError):
    """Base contract exception."""


class ContractViolationError(ContractError):
    """Framework contract violated."""