from __future__ import annotations

import time

from backend.application.services.llm_call_metrics import (
    LLMCallMetrics,
)
from backend.infrastructure.providers import (
    LLMProvider,
    ProviderFactory,
)


class LLMService:
    """
    Application service for LLM access.

    Responsibilities:
    - provide a single application-level interface for LLM calls;
    - count LLM calls;
    - collect per-call metrics;
    - collect token usage;
    - aggregate usage metrics;
    - track execution stage;
    - manage the active provider.
    """

    def __init__(
        self,
        provider: LLMProvider | None = None,
    ) -> None:

        self._provider = (
            provider
            if provider is not None
            else ProviderFactory.create()
        )

        self._call_count = 0

        self._call_metrics: list[
            LLMCallMetrics
        ] = []

    # ======================================================
    # Provider
    # ======================================================

    @property
    def provider(
        self,
    ) -> LLMProvider:

        return self._provider

    # ======================================================
    # LLM generation
    # ======================================================

    def generate(
        self,
        messages: list[dict[str, str]],
        *,
        stage: str | None = None,
        component: str | None = None,
    ) -> str:

        self._call_count += 1

        started_at = time.perf_counter()

        try:

            response = self._provider.generate(
                messages,
            )

        except Exception:

            duration = (
                time.perf_counter()
                - started_at
            )

            self._call_metrics.append(
                LLMCallMetrics(
                    stage=stage,
                    component=component,
                    duration=duration,
                    input_tokens=0,
                    output_tokens=0,
                    total_tokens=0,
                )
            )

            raise

        duration = (
            time.perf_counter()
            - started_at
        )

        input_tokens = (
            self._provider.last_input_tokens
        )

        output_tokens = (
            self._provider.last_output_tokens
        )

        total_tokens = (
            self._provider.last_total_tokens
        )

        self._call_metrics.append(
            LLMCallMetrics(
                stage=stage,
                component=component,
                duration=duration,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
            )
        )

        return response

    # ======================================================
    # Call metrics
    # ======================================================

    @property
    def call_count(
        self,
    ) -> int:

        return self._call_count

    def reset_call_count(
        self,
    ) -> None:

        self._call_count = 0
        self._call_metrics.clear()

    @property
    def call_metrics(
        self,
    ) -> list[LLMCallMetrics]:

        return list(
            self._call_metrics,
        )

    # ======================================================
    # Aggregated metrics
    # ======================================================

    @property
    def total_input_tokens(
        self,
    ) -> int:

        return sum(
            metric.input_tokens
            for metric in self._call_metrics
        )

    @property
    def total_output_tokens(
        self,
    ) -> int:

        return sum(
            metric.output_tokens
            for metric in self._call_metrics
        )

    @property
    def total_tokens(
        self,
    ) -> int:

        return sum(
            metric.total_tokens
            for metric in self._call_metrics
        )

    @property
    def total_duration(
        self,
    ) -> float:

        return sum(
            metric.duration
            for metric in self._call_metrics
        )

    def metrics_by_stage(
        self,
        stage: str,
    ) -> list[LLMCallMetrics]:

        return [
            metric
            for metric in self._call_metrics
            if metric.stage == stage
        ]

    def input_tokens_by_stage(
        self,
        stage: str,
    ) -> int:

        return sum(
            metric.input_tokens
            for metric in self.metrics_by_stage(
                stage,
            )
        )

    def output_tokens_by_stage(
        self,
        stage: str,
    ) -> int:

        return sum(
            metric.output_tokens
            for metric in self.metrics_by_stage(
                stage,
            )
        )

    def total_tokens_by_stage(
        self,
        stage: str,
    ) -> int:

        return sum(
            metric.total_tokens
            for metric in self.metrics_by_stage(
                stage,
            )
        )

    def duration_by_stage(
        self,
        stage: str,
    ) -> float:

        return sum(
            metric.duration
            for metric in self.metrics_by_stage(
                stage,
            )
        )

    def set_provider(
        self,
        provider: LLMProvider,
    ) -> None:

        self._provider = provider

    def metrics_by_component(
        self,
        component: str,
    ) -> list[LLMCallMetrics]:

        return [
            metric
            for metric in self._call_metrics
            if metric.component == component
        ]

    def duration_by_component(
        self,
        component: str,
    ) -> float:

        return sum(
            metric.duration
            for metric in self.metrics_by_component(
                component,
            )
        )

    def input_tokens_by_component(
        self,
        component: str,
    ) -> int:

        return sum(
            metric.input_tokens
            for metric in self.metrics_by_component(
                component,
            )
        )

    def output_tokens_by_component(
        self,
        component: str,
    ) -> int:

        return sum(
            metric.output_tokens
            for metric in self.metrics_by_component(
                component,
            )
        )

    def total_tokens_by_component(
        self,
        component: str,
    ) -> int:

        return sum(
            metric.total_tokens
            for metric in self.metrics_by_component(
                component,
            )
        )