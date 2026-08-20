from __future__ import annotations

from backend.benchmark.paradigms.paradigm_i.distributed_vote.components import DistributedVoteAggregatorComponent, DistributedVoteLLMComponent
from backend.components.benchmark.word_frequency.word_frequency_aggregator_component import WordFrequencyAggregatorComponent
from backend.components.benchmark.word_frequency.word_frequency_llm_component import WordFrequencyLLMComponent
from backend.components.flashcard.flashcard_component import FlashcardComponent
from backend.components.mentor.mentor_component import (
    MentorComponent,
)

from backend.components.benchmark.global_max.global_max_aggregator_component import (
    GlobalMaxAggregatorComponent,
)
from backend.components.benchmark.global_max.global_max_llm_component import (
    GlobalMaxLLMComponent,
)
from backend.components.planner.planner_component import PlannerComponent
from backend.components.quiz.quiz_component import QuizComponent
from backend.components.research.research_component import ResearchComponent
from backend.core.component_registry import (
    ComponentRegistry,
)


def register_components() -> None:
    """
    Register all application components.

    This function is idempotent and safe to call
    during application startup.
    """

    registrations = [
        MentorComponent,
        ResearchComponent,
        PlannerComponent,
        QuizComponent,
        FlashcardComponent,
        # GlobalMaxAggregatorComponent,
        # GlobalMaxLLMComponent,
        # WordFrequencyLLMComponent,
        # WordFrequencyAggregatorComponent,
        # DistributedVoteLLMComponent,
        # DistributedVoteAggregatorComponent
    ]

    for component in registrations:

        if ComponentRegistry.exists(
            component.component_id,
        ):
            continue

        ComponentRegistry.register(
            component,
        )