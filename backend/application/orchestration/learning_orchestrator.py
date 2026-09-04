
from __future__ import annotations

from backend.application.orchestration.adaptive_learning_pipeline import (
    AdaptiveLearningPipeline,
)
from backend.application.orchestration.adaptive_learning_result import (
    AdaptiveLearningResult,
)
from backend.application.orchestration.execution_request import (
    ExecutionRequest,
)
from backend.application.planning.planner import Planner
from backend.application.planning.planning_request import (
    PlanningRequest,
)
from backend.application.planning.workflow_builder import (
    WorkflowBuilder,
)
from backend.application.routing.router import Router
from backend.application.runtime.runtime import Runtime
from backend.application.runtime.runtime_context import (
    RuntimeContext,
)
from backend.application.runtime.runtime_result import (
    RuntimeResult,
)
from backend.application.services.memory_query_service import (
    MemoryQueryService,
)


class LearningOrchestrator:
    """
    Application-level coordinator.

    Coordinates the complete learning execution pipeline:

        ExecutionRequest
            ↓
        Routing
            ↓
        Adaptive Learning
            ↓
        Planning
            ↓
        Workflow Building
            ↓
        Runtime Context
            ↓
        Runtime Execution
            ↓
        RuntimeResult
    """

    def __init__(
        self,
        router: Router,
        planner: Planner,
        workflow_builder: WorkflowBuilder,
        runtime: Runtime,
        adaptive_learning_pipeline: AdaptiveLearningPipeline | None = None,
        memory_query_service: MemoryQueryService | None = None,
    ) -> None:

        self._router = router
        self._planner = planner
        self._workflow_builder = workflow_builder
        self._runtime = runtime

        self._adaptive_learning_pipeline = (
            adaptive_learning_pipeline
            if adaptive_learning_pipeline is not None
            else AdaptiveLearningPipeline()
        )

        self._memory_query_service = (
            memory_query_service
            if memory_query_service is not None
            else MemoryQueryService()
        )

    @staticmethod
    def _json_safe(
        value: object,
    ) -> object:
        """
        Convert nested runtime metadata into JSON-safe values.

        Handles:
        - Pydantic models;
        - datetime/date-like objects;
        - dictionaries;
        - lists/tuples;
        - nested combinations of the above.
        """

        if hasattr(
            value,
            "model_dump",
        ):
            return LearningOrchestrator._json_safe(
                value.model_dump()
            )

        if isinstance(
            value,
            dict,
        ):
            return {
                str(key): LearningOrchestrator._json_safe(
                    item
                )
                for key, item in value.items()
            }

        if isinstance(
            value,
            (list, tuple),
        ):
            return [
                LearningOrchestrator._json_safe(
                    item
                )
                for item in value
            ]

        if hasattr(
            value,
            "isoformat",
        ):
            return value.isoformat()

        return value

    def execute(
        self,
        request: ExecutionRequest,
    ) -> RuntimeResult:

        # ==================================================
        # 1. ROUTING
        # ==================================================

        routing_result = self._router.route(
            request.student,
            request.message,
        )

        # ==================================================
        # 2. CURRENT QUESTION / CONCEPTS
        # ==================================================

        current_question = request.metadata.get(
            "current_question",
            request.message,
        )

        current_concept_ids = request.metadata.get(
            "current_concept_ids",
            [],
        )

        # Defensive normalization.
        if not isinstance(
            current_concept_ids,
            list,
        ):
            current_concept_ids = []

        # ==================================================
        # 3. ADAPTIVE LEARNING
        # ==================================================

        adaptive_learning: AdaptiveLearningResult = (
            self._adaptive_learning_pipeline.run(
                learning_state=request.learning_state,
                current_question=current_question,
                related_concept_ids=current_concept_ids,
                primary_concept_ids=current_concept_ids,
            )
        )

        # ==================================================
        # 4. PLANNING
        # ==================================================

        planning_request = PlanningRequest(
            student=request.student,
            message=request.message,
            routing=routing_result,
            learning_state=request.learning_state,
            adaptive_learning=adaptive_learning,
        )

        plan = self._planner.plan(
            planning_request,
        )

        # ==================================================
        # 5. WORKFLOW BUILDING
        # ==================================================

        workflow = self._workflow_builder.build(
            plan,
        )

        # ==================================================
        # 6. RUNTIME CONTEXT
        # ==================================================

        context = RuntimeContext(
            workflow=workflow,
            learning_state=request.learning_state,
            adaptive_learning=adaptive_learning,
        )

        context.set_metadata(
            "student_id",
            request.student.id,
        )

        context.set_metadata(
            "message",
            request.message,
        )

        context.set_metadata(
            "current_question",
            current_question,
        )

        context.set_metadata(
            "current_concept_ids",
            current_concept_ids,
        )

        context.set_metadata(
            "routing",
            routing_result.model_dump(),
        )

        context.set_metadata(
            "historical_evidence",
            self._json_safe(
                adaptive_learning.evidence,
            ),
        )

        context.set_metadata(
            "knowledge_diagnosis",
            self._json_safe(
                adaptive_learning.diagnosis,
            ),
        )

        context.set_metadata(
            "adaptive_teaching_action",
            self._json_safe(
                adaptive_learning.teaching_action,
            ),
        )

        context.set_metadata(
            "adaptive_learning",
            self._json_safe(
                adaptive_learning,
            ),
        )

        # ==================================================
        # 6.1 HISTORICAL EVIDENCE / LONGTUTOR METADATA
        # ==================================================
        #
        # Preserve externally supplied historical evidence
        # inside the in-memory RuntimeContext.
        #
        # No repository.
        # No database.
        # No Gold answers.
        #
        # The Runtime/ContextBuilder will consume this metadata
        # through the canonical EvidenceSelector.
        # ==================================================

        request_metadata = request.metadata or {}

        for key in (
            "history_info",
            "history",
            "related_history",
            "longtutor_features",
        ):
            value = request_metadata.get(key)

            if value is not None:
                context.set_metadata(
                    key,
                    value,
                )

        # ==================================================
        # 6.2 MEMORY RETRIEVAL
        # ==================================================
        #
        # Each memory query is retrieved independently.
        #
        # The retrieval mode is intentionally separated from
        # answer generation:
        #
        #   context -> bounded Top-K evidence
        #   all     -> complete canonical evidence
        #
        # No Gold answer is ever passed to MemoryQueryService.
        # ==================================================

        memory_queries = request_metadata.get(
            "gold_memory_queries",
            [],
        )

        if not isinstance(
            memory_queries,
            list,
        ):
            memory_queries = []

        memory_retrieval = []

        for item in memory_queries:

            if isinstance(
                item,
                dict,
            ):
                query = item.get(
                    "query",
                    item.get(
                        "question",
                        "",
                    ),
                )

            elif isinstance(
                item,
                str,
            ):
                query = item

            else:
                query = ""

            query = str(
                query
                if query is not None
                else "",
            ).strip()

            if not query:
                continue

            retrieval_mode = (
                self._memory_query_service.infer_mode(
                    query,
                )
            )

            retrieval = (
                self._memory_query_service.retrieve(
                    learning_state=request.learning_state,
                    query=query,
                    history_info=context.get_metadata(
                        "history_info",
                        [],
                    ),
                    related_history=context.get_metadata(
                        "related_history",
                        [],
                    ),
                    mode=retrieval_mode,
                )
            )

            memory_retrieval.append(
                {
                    "query": query,
                    "mode": retrieval["mode"],
                    "evidence": retrieval["history"],
                    "related_evidence": retrieval[
                        "related_history"
                    ],
                    "stats": retrieval["stats"],
                }
            )

        # ==================================================
        # IMPORTANT:
        # Serialize memory retrieval at the application
        # boundary before it enters RuntimeContext.
        #
        # This prevents LearningInteraction / datetime /
        # nested Pydantic objects from reaching Runner JSON
        # serialization.
        # ==================================================

        context.set_metadata(
            "memory_retrieval",
            self._json_safe(
                memory_retrieval,
            ),
        )

        # ==================================================
        # 7. DEBUG
        # ==================================================

        print(
            "ROUTING:",
            routing_result.model_dump(),
        )

        print(
            "CURRENT QUESTION:",
            current_question,
        )

        print(
            "CURRENT CONCEPTS:",
            current_concept_ids,
        )

        print(
            "ADAPTIVE LEARNING:",
            adaptive_learning.model_dump(),
        )

        print(
            "PLAN:",
            plan.model_dump(),
        )

        print(
            "WORKFLOW NODES:",
            [
                {
                    "id": node.id,
                    "component": node.component_id,
                    "objective": node.objective,
                    "action": node.action,
                    "strategy": node.strategy,
                    "difficulty": node.difficulty,
                    "focus_concepts": node.focus_concepts,
                }
                for node in workflow.nodes
            ],
        )

        # ==================================================
        # 7.1 DEBUG RUNTIME EVIDENCE
        # ==================================================

        history_info = context.get_metadata(
            "history_info",
            [],
        )

        history = context.get_metadata(
            "history",
            [],
        )

        related_history = context.get_metadata(
            "related_history",
            [],
        )

        longtutor_features = context.get_metadata(
            "longtutor_features",
            {},
        )

        print(
            "RUNTIME HISTORY INFO:",
            len(history_info)
            if isinstance(
                history_info,
                list,
            )
            else 0,
        )

        print(
            "RUNTIME HISTORY:",
            len(history)
            if isinstance(
                history,
                list,
            )
            else 0,
        )

        print(
            "RUNTIME RELATED HISTORY:",
            len(related_history)
            if isinstance(
                related_history,
                list,
            )
            else 0,
        )

        print(
            "RUNTIME LONGTUTOR FEATURES:",
            bool(longtutor_features),
        )

        # ==================================================
        # 8. RUNTIME EXECUTION
        # ==================================================

        return self._runtime.run(
            context,
        )

