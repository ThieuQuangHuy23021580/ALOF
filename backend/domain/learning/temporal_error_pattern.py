from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from math import exp, log2

from backend.domain.learning.learning_interaction import (
    LearningInteraction,
)


@dataclass(frozen=True)
class TemporalErrorPattern:
    concept_id: str

    pattern: str

    persistence_score: float = 0.0
    recovery_score: float = 0.0
    instability_score: float = 0.0
    recent_error_pressure: float = 0.0

    observation_count: int = 0
    error_count: int = 0
    correct_count: int = 0

    transition_counts: dict[str, int] | None = None

    confidence: float = 0.0

    def as_dict(self) -> dict[str, object]:
        return {
            "concept_id": self.concept_id,
            "pattern": self.pattern,
            "persistence_score": self.persistence_score,
            "recovery_score": self.recovery_score,
            "instability_score": self.instability_score,
            "recent_error_pressure": self.recent_error_pressure,
            "observation_count": self.observation_count,
            "error_count": self.error_count,
            "correct_count": self.correct_count,
            "transition_counts": (
                dict(self.transition_counts or {})
            ),
            "confidence": self.confidence,
        }


class TemporalErrorPatternDetector:
    """
    Deterministic temporal error-pattern detector.

    The detector models correctness as a temporal sequence instead of
    treating historical answers as independent observations.

    Signals:
    - recent error pressure
    - persistent error behavior
    - recovery after errors
    - transition instability
    - observation confidence

    Patterns:
    - persistent
    - recovering
    - unstable
    - stable
    """

    def __init__(
        self,
        recency_decay: float = 0.1,
        recency_unit_seconds: float = 86400.0,
        minimum_observations: int = 3,
        persistence_threshold: float = 0.60,
        recovery_threshold: float = 0.55,
        instability_threshold: float = 0.65,
        confidence_k: float = 5.0,
    ) -> None:

        if recency_decay < 0.0:
            raise ValueError(
                "recency_decay must be non-negative."
            )

        if recency_unit_seconds <= 0.0:
            raise ValueError(
                "recency_unit_seconds must be greater than 0."
            )

        if minimum_observations < 2:
            raise ValueError(
                "minimum_observations must be at least 2."
            )

        if not 0.0 <= persistence_threshold <= 1.0:
            raise ValueError(
                "persistence_threshold must be between 0 and 1."
            )

        if not 0.0 <= recovery_threshold <= 1.0:
            raise ValueError(
                "recovery_threshold must be between 0 and 1."
            )

        if not 0.0 <= instability_threshold <= 1.0:
            raise ValueError(
                "instability_threshold must be between 0 and 1."
            )

        if confidence_k <= 0.0:
            raise ValueError(
                "confidence_k must be greater than 0."
            )

        self._recency_decay = recency_decay
        self._recency_unit_seconds = (
            recency_unit_seconds
        )
        self._minimum_observations = (
            minimum_observations
        )
        self._persistence_threshold = (
            persistence_threshold
        )
        self._recovery_threshold = (
            recovery_threshold
        )
        self._instability_threshold = (
            instability_threshold
        )
        self._confidence_k = confidence_k

    def detect(
        self,
        concept_id: str,
        interactions: list[LearningInteraction],
        reference_time: datetime | None = None,
    ) -> TemporalErrorPattern:

        observations = self._prepare_observations(
            concept_id=concept_id,
            interactions=interactions,
        )

        if not observations:
            return TemporalErrorPattern(
                concept_id=concept_id,
                pattern="stable",
            )

        now = reference_time or self._reference_time(
            observations
        )

        correctness = [
            bool(interaction.correct)
            for interaction in observations
            if interaction.correct is not None
        ]

        error_count = sum(
            1
            for interaction in observations
            if interaction.correct is False
        )

        correct_count = sum(
            1
            for interaction in observations
            if interaction.correct is True
        )

        recent_error_pressure = (
            self._recent_error_pressure(
                observations=observations,
                reference_time=now,
            )
        )

        persistence_score = (
            self._persistence_score(
                correctness=correctness,
                observations=observations,
                reference_time=now,
            )
        )

        recovery_score = (
            self._recovery_score(
                correctness=correctness,
                observations=observations,
            )
        )

        transition_counts = (
            self._transition_counts(
                correctness
            )
        )

        instability_score = (
            self._transition_entropy(
                transition_counts
            )
        )

        confidence = (
            len(correctness)
            / (
                len(correctness)
                + self._confidence_k
            )
        )

        pattern = self._classify(
            observation_count=len(correctness),
            persistence_score=persistence_score,
            recovery_score=recovery_score,
            instability_score=instability_score,
            recent_error_pressure=recent_error_pressure,
        )

        return TemporalErrorPattern(
            concept_id=concept_id,
            pattern=pattern,
            persistence_score=persistence_score,
            recovery_score=recovery_score,
            instability_score=instability_score,
            recent_error_pressure=recent_error_pressure,
            observation_count=len(correctness),
            error_count=error_count,
            correct_count=correct_count,
            transition_counts=transition_counts,
            confidence=confidence,
        )

    def _prepare_observations(
        self,
        concept_id: str,
        interactions: list[LearningInteraction],
    ) -> list[LearningInteraction]:

        result: list[LearningInteraction] = []
        seen: set[str] = set()

        for interaction in interactions:

            if interaction.id in seen:
                continue

            if interaction.correct is None:
                continue

            if concept_id not in {
                str(value)
                for value in interaction.concept_ids
                if value is not None
            }:
                continue

            seen.add(interaction.id)
            result.append(interaction)

        result.sort(
            key=lambda interaction: interaction.timestamp
        )

        return result

    @staticmethod
    def _reference_time(
        interactions: list[LearningInteraction],
    ) -> datetime:

        latest = max(
            interaction.timestamp
            for interaction in interactions
        )

        if latest.tzinfo is None:
            return latest.replace(tzinfo=UTC)

        return latest

    def _recent_error_pressure(
        self,
        observations: list[LearningInteraction],
        reference_time: datetime,
    ) -> float:

        weighted_errors = 0.0
        total_weight = 0.0

        for interaction in observations:

            age_seconds = (
                reference_time
                - self._normalize_datetime(
                    interaction.timestamp
                )
            ).total_seconds()

            age_seconds = max(
                0.0,
                age_seconds,
            )

            age_units = (
                age_seconds
                / self._recency_unit_seconds
            )

            weight = exp(
                -self._recency_decay * age_units
            )

            total_weight += weight

            if interaction.correct is False:
                weighted_errors += weight

        if total_weight <= 0.0:
            return 0.0

        return self._clamp(
            weighted_errors / total_weight
        )

    def _persistence_score(
        self,
        correctness: list[bool],
        observations: list[LearningInteraction],
        reference_time: datetime,
    ) -> float:

        if not correctness:
            return 0.0

        longest_error_run = 0
        current_error_run = 0

        for value in correctness:

            if not value:
                current_error_run += 1
                longest_error_run = max(
                    longest_error_run,
                    current_error_run,
                )
            else:
                current_error_run = 0

        run_strength = (
            longest_error_run
            / len(correctness)
        )

        weighted_pressure = (
            self._recent_error_pressure(
                observations=observations,
                reference_time=reference_time,
            )
        )

        persistence = (
            0.55 * run_strength
            + 0.45 * weighted_pressure
        )

        return self._clamp(persistence)

    @staticmethod
    def _recovery_score(
        correctness: list[bool],
        observations: list[LearningInteraction],
    ) -> float:

        if len(correctness) < 2:
            return 0.0

        recovery_events = 0
        error_events = 0

        for previous, current in zip(
            correctness,
            correctness[1:],
        ):

            if not previous:
                error_events += 1

                if current:
                    recovery_events += 1

        if error_events == 0:
            return 0.0

        transition_recovery = (
            recovery_events
            / error_events
        )

        recent_correct_run = 0

        for value in reversed(correctness):
            if value:
                recent_correct_run += 1
            else:
                break

        recent_recovery_strength = (
            min(
                1.0,
                recent_correct_run / 3.0,
            )
        )

        recovery = (
            0.65 * transition_recovery
            + 0.35 * recent_recovery_strength
        )

        return TemporalErrorPatternDetector._clamp(
            recovery
        )

    @staticmethod
    def _transition_counts(
        correctness: list[bool],
    ) -> dict[str, int]:

        counts = Counter()

        for previous, current in zip(
            correctness,
            correctness[1:],
        ):

            previous_state = (
                "C" if previous else "W"
            )

            current_state = (
                "C" if current else "W"
            )

            counts[
                f"{previous_state}{current_state}"
            ] += 1

        return {
            key: int(value)
            for key, value in sorted(
                counts.items()
            )
        }

    @staticmethod
    def _transition_entropy(
        transition_counts: dict[str, int],
    ) -> float:

        total = sum(
            transition_counts.values()
        )

        if total <= 0:
            return 0.0

        entropy = 0.0

        for count in transition_counts.values():

            if count <= 0:
                continue

            probability = count / total

            entropy -= (
                probability
                * log2(probability)
            )

        # Four possible transitions:
        # CC, CW, WC, WW.
        # Normalize entropy to [0, 1].
        maximum_entropy = 2.0

        return TemporalErrorPatternDetector._clamp(
            entropy / maximum_entropy
        )

    def _classify(
        self,
        observation_count: int,
        persistence_score: float,
        recovery_score: float,
        instability_score: float,
        recent_error_pressure: float,
    ) -> str:

        if observation_count < self._minimum_observations:
            return "stable"

        if (
            instability_score
            >= self._instability_threshold
            and recent_error_pressure >= 0.30
        ):
            return "unstable"

        if (
            recovery_score
            >= self._recovery_threshold
            and persistence_score
            < self._persistence_threshold
        ):
            return "recovering"

        if (
            persistence_score
            >= self._persistence_threshold
            and recovery_score
            < self._recovery_threshold
        ):
            return "persistent"

        if (
            recent_error_pressure
            >= 0.65
            and recovery_score < 0.40
        ):
            return "persistent"

        if (
            recovery_score >= 0.70
            and recent_error_pressure < 0.40
        ):
            return "recovering"

        return "stable"

    @staticmethod
    def _normalize_datetime(
        value: datetime,
    ) -> datetime:

        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)

        return value

    @staticmethod
    def _clamp(
        value: float,
    ) -> float:

        return max(
            0.0,
            min(
                1.0,
                value,
            ),
        )