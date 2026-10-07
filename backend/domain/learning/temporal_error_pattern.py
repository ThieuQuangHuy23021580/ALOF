from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from math import exp, log, log1p, log2
from statistics import median

from backend.domain.learning.learning_interaction import LearningInteraction


@dataclass(frozen=True)
class TemporalErrorPattern:
    concept_id: str
    pattern: str
    persistence_score: float = 0.0
    recovery_score: float = 0.0
    instability_score: float = 0.0
    recent_error_pressure: float = 0.0
    retention_risk: float = 0.0
    retention_strength: float = 1.0
    estimated_half_life_days: float = 1.0
    time_since_last_success_days: float = 0.0
    spacing_strength: float = 0.0
    error_amplification: float = 1.0
    next_error_risk: float = 0.0
    next_error_risk_after_error: float = 0.0
    next_error_risk_after_correct: float = 0.0
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
            "retention_risk": self.retention_risk,
            "retention_strength": self.retention_strength,
            "estimated_half_life_days": self.estimated_half_life_days,
            "time_since_last_success_days": (
                self.time_since_last_success_days
            ),
            "spacing_strength": self.spacing_strength,
            "error_amplification": self.error_amplification,
            "next_error_risk": self.next_error_risk,
            "next_error_risk_after_error": (
                self.next_error_risk_after_error
            ),
            "next_error_risk_after_correct": (
                self.next_error_risk_after_correct
            ),
            "observation_count": self.observation_count,
            "error_count": self.error_count,
            "correct_count": self.correct_count,
            "transition_counts": dict(self.transition_counts or {}),
            "confidence": self.confidence,
        }


class TemporalErrorPatternDetector:
    """
    Deterministic temporal error-pattern and retention detector.

    The detector models correctness as a temporal sequence
    instead of treating historical answers as independent
    observations.

    Signals:
    - recent error pressure;
    - persistent error behavior;
    - recovery after errors;
    - transition instability;
    - personalized retention strength;
    - forgetting / retention risk;
    - next-error risk;
    - observation confidence.

    Retention uses an exponential forgetting curve:

        R(t) = exp(-ln(2) * t / H)

    where H is an estimated concept-specific retention
    half-life.

    Next-error risk uses a first-order Markov transition
    estimate with Laplace smoothing:

        P(W_next | W_current)
        P(W_next | C_current)

    The final next-error risk is conditioned on the
    learner's latest observed state.

    Patterns:
    - persistent
    - recovering
    - unstable
    - stable

    The detector is deterministic, read-only, and does not
    call an LLM.
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
        minimum_half_life_days: float = 0.5,
        maximum_half_life_days: float = 60.0,
        transition_smoothing: float = 1.0,
    ) -> None:
        if recency_decay < 0.0:
            raise ValueError("recency_decay must be non-negative.")

        if recency_unit_seconds <= 0.0:
            raise ValueError(
                "recency_unit_seconds must be greater than 0."
            )

        if minimum_observations < 2:
            raise ValueError("minimum_observations must be at least 2.")

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
            raise ValueError("confidence_k must be greater than 0.")

        if minimum_half_life_days <= 0.0:
            raise ValueError(
                "minimum_half_life_days must be greater than 0."
            )

        if maximum_half_life_days < minimum_half_life_days:
            raise ValueError(
                "maximum_half_life_days must be greater than "
                "or equal to minimum_half_life_days."
            )

        if transition_smoothing <= 0.0:
            raise ValueError(
                "transition_smoothing must be greater than 0."
            )

        self._recency_decay = recency_decay
        self._recency_unit_seconds = recency_unit_seconds
        self._minimum_observations = minimum_observations
        self._persistence_threshold = persistence_threshold
        self._recovery_threshold = recovery_threshold
        self._instability_threshold = instability_threshold
        self._confidence_k = confidence_k
        self._minimum_half_life_days = minimum_half_life_days
        self._maximum_half_life_days = maximum_half_life_days
        self._transition_smoothing = transition_smoothing

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

        now = reference_time or self._reference_time(observations)

        correctness = [
            interaction.correct
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

        recent_error_pressure = self._recent_error_pressure(
            observations=observations,
            reference_time=now,
        )

        persistence_score = self._persistence_score(
            correctness=correctness,
            observations=observations,
            reference_time=now,
        )

        recovery_score = self._recovery_score(correctness=correctness)

        transition_counts = self._transition_counts(correctness)

        instability_score = self._transition_entropy(transition_counts)

        (
            next_error_risk,
            next_error_risk_after_error,
            next_error_risk_after_correct,
        ) = self._next_error_risk(
            correctness=correctness,
            transition_counts=transition_counts,
        )

        (
            estimated_half_life_days,
            spacing_strength,
            error_amplification,
        ) = self._estimate_retention_parameters(
            observations=observations,
            persistence_score=persistence_score,
            recovery_score=recovery_score,
        )

        (
            retention_risk,
            retention_strength,
            time_since_last_success_days,
        ) = self._retention_risk(
            observations=observations,
            reference_time=now,
            half_life_days=estimated_half_life_days,
            error_amplification=error_amplification,
            persistence_score=persistence_score,
            instability_score=instability_score,
        )

        confidence = len(correctness) / (
            len(correctness) + self._confidence_k
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
            retention_risk=retention_risk,
            retention_strength=retention_strength,
            estimated_half_life_days=estimated_half_life_days,
            time_since_last_success_days=time_since_last_success_days,
            spacing_strength=spacing_strength,
            error_amplification=error_amplification,
            next_error_risk=next_error_risk,
            next_error_risk_after_error=next_error_risk_after_error,
            next_error_risk_after_correct=next_error_risk_after_correct,
            observation_count=len(correctness),
            error_count=error_count,
            correct_count=correct_count,
            transition_counts=transition_counts,
            confidence=confidence,
        )

    def _classify(
        self,
        *,
        observation_count: int,
        persistence_score: float,
        recovery_score: float,
        instability_score: float,
        recent_error_pressure: float,
    ) -> str:
        """
        Combine detector signals into a coarse temporal pattern label.

        Order of precedence (highest first):
            1. unstable        — high transition entropy
            2. persistent      — high persistence + recent pressure
            3. recovering      — recovery dominates persistence
            5. stable          — default fallback
        """
        if observation_count < self._minimum_observations:
            return "stable"

        if instability_score >= self._instability_threshold:
            return "unstable"

        if (
            persistence_score >= self._persistence_threshold
            and recent_error_pressure >= self._persistence_threshold
        ):
            return "persistent"

        if (
            recovery_score >= self._recovery_threshold
            and recovery_score > persistence_score
        ):
            return "recovering"

        return "stable"

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

        result.sort(key=lambda interaction: interaction.timestamp)

        return result

    @staticmethod
    def _clamp(
        value: float,
        minimum: float = 0.0,
        maximum: float = 1.0,
    ) -> float:
        return min(max(value, minimum), maximum)

    @staticmethod
    def _normalize_datetime(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    @staticmethod
    def _reference_time(
        interactions: list[LearningInteraction],
    ) -> datetime:
        latest = max(
            interaction.timestamp for interaction in interactions
        )
        return TemporalErrorPatternDetector._normalize_datetime(latest)

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
                - self._normalize_datetime(interaction.timestamp)
            ).total_seconds()

            age_seconds = max(0.0, age_seconds)

            age_units = age_seconds / self._recency_unit_seconds

            weight = exp(-self._recency_decay * age_units)

            total_weight += weight

            if interaction.correct is False:
                weighted_errors += weight

        if total_weight <= 0.0:
            return 0.0

        return self._clamp(weighted_errors / total_weight)

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

        run_strength = longest_error_run / len(correctness)

        weighted_pressure = self._recent_error_pressure(
            observations=observations,
            reference_time=reference_time,
        )

        persistence = 0.55 * run_strength + 0.45 * weighted_pressure

        return self._clamp(persistence)

    @staticmethod
    def _recovery_score(correctness: list[bool]) -> float:
        if len(correctness) < 2:
            return 0.0

        recovery_events = 0
        error_events = 0

        for previous, current in zip(correctness, correctness[1:]):
            if not previous:
                error_events += 1

                if current:
                    recovery_events += 1

        if error_events == 0:
            return 0.0

        transition_recovery = recovery_events / error_events

        recent_correct_run = 0

        for value in reversed(correctness):
            if value:
                recent_correct_run += 1
            else:
                break

        recent_recovery_strength = min(
            1.0,
            recent_correct_run / 3.0,
        )

        recovery = (
            0.65 * transition_recovery
            + 0.35 * recent_recovery_strength
        )

        return TemporalErrorPatternDetector._clamp(recovery)

    @staticmethod
    def _transition_counts(correctness: list[bool]) -> dict[str, int]:
        counts = Counter()

        for previous, current in zip(correctness, correctness[1:]):
            previous_state = "C" if previous else "W"
            current_state = "C" if current else "W"

            counts[f"{previous_state}{current_state}"] += 1

        for key in ("CC", "CW", "WC", "WW"):
            counts.setdefault(key, 0)

        return {
            key: int(value)
            for key, value in sorted(counts.items())
        }

    def _next_error_risk(
        self,
        correctness: list[bool],
        transition_counts: dict[str, int],
    ) -> tuple[float, float, float]:
        if not correctness:
            return (0.0, 0.0, 0.0)

        alpha = self._transition_smoothing

        ww = float(transition_counts.get("WW", 0))
        wc = float(transition_counts.get("WC", 0))
        cw = float(transition_counts.get("CW", 0))
        cc = float(transition_counts.get("CC", 0))

        next_error_after_error = (ww + alpha) / (
            ww + wc + 2.0 * alpha
        )

        next_error_after_correct = (cw + alpha) / (
            cw + cc + 2.0 * alpha
        )

        latest_state = correctness[-1]

        if latest_state:
            next_error_risk = next_error_after_correct
        else:
            next_error_risk = next_error_after_error

        return (
            self._clamp(next_error_risk),
            self._clamp(next_error_after_error),
            self._clamp(next_error_after_correct),
        )

    @staticmethod
    def _transition_entropy(
        transition_counts: dict[str, int],
    ) -> float:
        total = sum(transition_counts.values())

        if total <= 0:
            return 0.0

        entropy = 0.0

        for count in transition_counts.values():
            if count <= 0:
                continue

            probability = count / total

            entropy -= probability * log2(probability)

        maximum_entropy = 2.0

        return TemporalErrorPatternDetector._clamp(
            entropy / maximum_entropy,
        )

    def _estimate_retention_parameters(
        self,
        observations: list[LearningInteraction],
        persistence_score: float,
        recovery_score: float,
    ) -> tuple[float, float, float]:
        successful = [
            interaction
            for interaction in observations
            if interaction.correct is True
        ]

        successful_intervals: list[float] = []

        for previous, current in zip(successful, successful[1:]):
            previous_time = self._normalize_datetime(
                previous.timestamp,
            )

            current_time = self._normalize_datetime(
                current.timestamp,
            )

            interval_days = (
                current_time - previous_time
            ).total_seconds() / 86400.0

            if interval_days > 0.0:
                successful_intervals.append(interval_days)

        if successful_intervals:
            typical_spacing = median(successful_intervals)
        else:
            typical_spacing = 1.0

        typical_spacing = min(
            max(
                typical_spacing,
                self._minimum_half_life_days,
            ),
            self._maximum_half_life_days,
        )

        success_ratio = len(successful) / max(len(observations), 1)

        practice_stability = self._clamp(
            0.55 * success_ratio
            + 0.45
            * (
                1.0
                - exp(-0.35 * log1p(len(successful)))
            )
        )

        spacing_strength = self._clamp(
            0.50 * (typical_spacing / (typical_spacing + 7.0))
            + 0.50 * practice_stability
        )

        base_half_life = typical_spacing * (
            1.0 + 0.75 * practice_stability
        )

        error_amplification = (
            1.0
            + 0.80 * persistence_score
            + 0.40 * (1.0 - recovery_score)
        )

        adjusted_half_life = base_half_life / error_amplification

        adjusted_half_life = min(
            max(
                adjusted_half_life,
                self._minimum_half_life_days,
            ),
            self._maximum_half_life_days,
        )

        return (
            adjusted_half_life,
            spacing_strength,
            error_amplification,
        )

    def _retention_risk(
        self,
        observations: list[LearningInteraction],
        reference_time: datetime,
        half_life_days: float,
        error_amplification: float,
        persistence_score: float,
        instability_score: float,
    ) -> tuple[float, float, float]:
        successful = [
            interaction
            for interaction in observations
            if interaction.correct is True
        ]

        if successful:
            last_success = successful[-1]
            last_success_time = self._normalize_datetime(
                last_success.timestamp,
            )
            time_since_success_days = max(
                0.0,
                (
                    reference_time - last_success_time
                ).total_seconds() / 86400.0,
            )
        else:
            last_interaction = observations[-1]
            last_interaction_time = self._normalize_datetime(
                last_interaction.timestamp,
            )
            time_since_success_days = max(
                0.0,
                (
                    reference_time - last_interaction_time
                ).total_seconds() / 86400.0,
            )

        retention_strength = exp(
            -log(2.0) * time_since_success_days / max(half_life_days, 1e-6)
        )
        forgetting = 1.0 - retention_strength
        retention_risk = self._clamp(
            forgetting
            * (
                0.55
                + 0.20 * error_amplification / (1.0 + error_amplification)
                + 0.15 * persistence_score
                + 0.10 * instability_score
            )
        )
        return (
            retention_risk,
            self._clamp(retention_strength),
            time_since_success_days,
        )