from __future__ import annotations

import logging
import os
import re
import time
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Pattern: "Please try again in XmYs.Zs" or "try again in Xs"
_RETRY_AFTER = re.compile(r"try again in (\d+(?:\.\d+)?)\s*[ms]", re.IGNORECASE)


# Default 3 models used per API key (priority-ordered, lower = tried first).
DEFAULT_MODELS: list[tuple[str, int]] = [
    ("openai/gpt-oss-120b", 0),
    ("openai/gpt-oss-20b", 1),
    ("qwen/qwen3.8-27b", 2),
]

# Ordered list of env-var names containing API keys, used in this exact
# sequential order by the fallback manager.
DEFAULT_KEY_ORDER: list[str] = [
    "GROQ_API_KEY",
    "NEW_GROQ_API_KEY",
    "GROQ_API_KEY_1",
    "GROQ_API_KEY_2",
    "GROQ_API_KEY_3",
]

# Per-key model overrides. Format: GROQ_KEY_MODELS_<n>="m1,m2,m3"
# The suffix matches the key position in DEFAULT_KEY_ORDER (0-indexed).
# Example:
#     GROQ_KEY_MODELS_0=openai/gpt-oss-120b,qwen/qwen3.8-27b
#     GROQ_KEY_MODELS_2=openai/gpt-oss-20b


@dataclass
class ModelConfig:
    name: str
    priority: int = 0

    def __lt__(self, other: "ModelConfig") -> bool:
        return self.priority < other.priority


@dataclass
class APIKeyConfig:
    """
    One Groq API key plus the list of models we will try against it.

    Fields:
        slot: positional index in the key ordering (0..N-1)
        env_var: actual env var name (e.g. ``GROQ_API_KEY_1``)
        key: the API key string itself
        label: human-readable label for logging (e.g. ``KEY_0``, ``NEW``)
        models: ordered list of ModelConfig
    """

    slot: int
    env_var: str
    key: str
    label: str
    models: list[ModelConfig] = field(default_factory=list)

    @property
    def available_models(self) -> list[str]:
        return [m.name for m in sorted(self.models)]


class APIFallbackManager:
    """
    Sequentially rotates through a fixed list of Groq API keys, trying
    multiple models against each key before moving on.

    Order of attempts is **strictly sequential and predictable**:

        KEY[0] + model_0 → KEY[0] + model_1 → KEY[0] + model_2
        → KEY[1] + model_0 → KEY[1] + model_1 → KEY[1] + model_2
        → ...

    Configuration (all env-vars; do not edit code):

        GROQ_API_KEY, NEW_GROQ_API_KEY, GROQ_API_KEY_1, ...    keys (in order)
        GROQ_KEY_ORDER                comma-separated override of key order
        GROQ_KEY_MODELS_<slot>        comma-separated models for that slot
        GROQ_MODEL_DEFAULT_1, _2, _3  default 3-model list (priority 0,1,2)

    Per-key model assignment:
        GROQ_KEY_MODELS_0=openai/gpt-oss-120b,openai/gpt-oss-20b
        GROQ_KEY_MODELS_2=qwen/qwen3.8-27b

    If no per-key override is set, all keys use the same default
    3-model list (gpt-oss-120b → gpt-oss-20b → qwen/qwen3.8-27b).
    """

    def __init__(
        self,
        max_retries_per_call: int | None = None,
        retry_delay: float | None = None,
    ) -> None:
        env_retries = os.environ.get(
            "GROQ_FALLBACK_MAX_RETRIES",
            "",
        ).strip()
        if env_retries and max_retries_per_call is None:
            try:
                max_retries_per_call = int(env_retries)
            except ValueError:
                max_retries_per_call = 3
        if max_retries_per_call is None:
            max_retries_per_call = 3

        env_delay = os.environ.get(
            "GROQ_FALLBACK_RETRY_DELAY",
            "",
        ).strip()
        if env_delay and retry_delay is None:
            try:
                retry_delay = float(env_delay)
            except ValueError:
                retry_delay = 20.0
        if retry_delay is None:
            retry_delay = 20.0

        self.max_retries = max_retries_per_call
        self.retry_delay = retry_delay

        self._keys: list[APIKeyConfig] = []
        self._load_keys()

        self._call_count: int = 0
        self._fail_count: int = 0
        self._current_slot: int = 0
        self._exhausted_keys: set[int] = set()  # slots whose TPD/quota is exhausted

    # ----------------------------------------------------------
    # Loading
    # ----------------------------------------------------------

    def _load_keys(self) -> None:
        """Load keys in declared sequential order."""
        order_env = os.environ.get("GROQ_KEY_ORDER", "")
        if order_env.strip():
            order = [
                name.strip()
                for name in order_env.split(",")
                if name.strip()
            ]
        else:
            order = list(DEFAULT_KEY_ORDER)

        seen: set[str] = set()
        deduped_order: list[str] = []
        for name in order:
            if name in seen:
                continue
            seen.add(name)
            deduped_order.append(name)

        slot = 0
        for env_var in deduped_order:
            value = os.environ.get(env_var, "").strip()
            if not value:
                continue

            label = self._key_label(env_var, slot)
            cfg = APIKeyConfig(
                slot=slot,
                env_var=env_var,
                key=value,
                label=label,
            )
            cfg.models.extend(
                self._load_models_for_slot(slot),
            )
            self._keys.append(cfg)
            slot += 1

        if not self._keys:
            raise RuntimeError(
                "No API keys found. "
                "Set at least one of: " + ", ".join(DEFAULT_KEY_ORDER)
            )

        logger.info(
            "APIFallbackManager loaded %d key(s) in sequential order:",
            len(self._keys),
        )
        for cfg in self._keys:
            logger.info(
                "  slot %d  %s  (%s)  models=%s",
                cfg.slot,
                cfg.env_var,
                cfg.label,
                cfg.available_models,
            )

    @staticmethod
    def _key_label(env_var: str, slot: int) -> str:
        """Short human-readable label for logging."""
        if env_var == "GROQ_API_KEY":
            return "PRIMARY"
        if env_var == "NEW_GROQ_API_KEY":
            return "BACKUP_NEW"
        if env_var.startswith("GROQ_API_KEY_"):
            return f"KEY_{env_var.split('_')[-1]}"
        return f"KEY_{slot}"

    def _load_models_for_slot(
        self,
        slot: int,
    ) -> list[ModelConfig]:
        """Read per-slot model override, else default 3-model list."""
        override = os.environ.get(
            f"GROQ_KEY_MODELS_{slot}",
            "",
        ).strip()

        if override:
            models: list[ModelConfig] = []
            for priority, raw in enumerate(
                override.split(","),
            ):
                name = raw.strip()
                if name:
                    models.append(
                        ModelConfig(
                            name=name,
                            priority=priority,
                        )
                    )
            return models

        return [
            ModelConfig(name=name, priority=prio)
            for name, prio in DEFAULT_MODELS
        ]

    # ----------------------------------------------------------
    # Accessors
    # ----------------------------------------------------------

    @property
    def keys(self) -> list[APIKeyConfig]:
        return self._keys

    @property
    def current_slot(self) -> int:
        return self._current_slot

    @property
    def stats(self) -> dict[str, int]:
        return {
            "total_calls": self._call_count,
            "total_fails": self._fail_count,
        }

    def get_client_config(
        self,
        slot: int,
        model_name: str,
    ) -> dict:
        cfg = next(
            (k for k in self._keys if k.slot == slot),
            None,
        )
        if cfg is None:
            raise ValueError(
                f"No APIKeyConfig for slot {slot}"
            )
        return {
            "api_key": cfg.key,
            "base_url": "https://api.groq.com/openai/v1",
            "model": model_name,
            "env_var": cfg.env_var,
            "slot": cfg.slot,
            "label": cfg.label,
        }

    # ----------------------------------------------------------
    # Fallback loop
    # ----------------------------------------------------------

    def execute_with_fallback(
        self,
        call_fn,
        extra_attempts: int = 0,
    ) -> tuple[str, int, str]:
        """
        Call ``call_fn(client_kwargs: dict)`` with sequential fallback.

        Args:
            call_fn: callable accepting dict
                ``{"api_key", "base_url", "model",
                   "env_var", "slot", "label"}``
                and returning the LLM response.
            extra_attempts: extra tries beyond ``max_retries``.

        Returns:
            (response, final_slot, final_model_name)

        Raises:
            The last exception if all keys and models are exhausted.

        Iteration order for 5 keys × 3 models each::

            PRIMARY  + gpt-oss-120b
            PRIMARY  + gpt-oss-20b
            PRIMARY  + qwen/qwen3.8-27b
            BACKUP_NEW + gpt-oss-120b
            BACKUP_NEW + gpt-oss-20b
            BACKUP_NEW + qwen/qwen3.8-27b
            KEY_1    + gpt-oss-120b
            ... etc.
        """
        max_attempts = self.max_retries + extra_attempts
        total_tried: set[tuple[int, str]] = set()
        # Track models tried per key to detect when an entire key is exhausted.
        models_per_key: dict[int, set[str]] = {}

        attempt = 0
        last_exc: Exception | None = None

        while attempt < max_attempts:
            self._call_count += 1

            slot, model = self._get_next_candidate(
                total_tried,
                skip_slots=self._exhausted_keys,
            )
            if slot is None:
                # No more combinations to try — raise immediately.
                break

            cfg = next(k for k in self._keys if k.slot == slot)
            client_kwargs = self.get_client_config(slot, model)

            try:
                result = call_fn(client_kwargs)
                self._current_slot = slot
                logger.debug(
                    "APIFallback: succeeded with %s / %s",
                    cfg.label,
                    model,
                )
                return result, slot, model

            except Exception as exc:  # noqa: BLE001
                self._fail_count += 1
                last_exc = exc
                error_str = str(exc).lower()
                should_fallback = self._should_fallback(
                    exc,
                    error_str,
                )

                if not should_fallback:
                    logger.error(
                        "APIFallback: non-retriable error on "
                        "%s / %s — %s",
                        cfg.label,
                        model,
                        exc,
                    )
                    raise

                total_tried.add((slot, model))
                models_per_key.setdefault(slot, set()).add(model)
                is_quota_exhausted = self._is_quota_exhausted(error_str)
                is_key_exhausted = (
                    is_quota_exhausted
                    and models_per_key[slot]
                    == {m.name for m in cfg.models}
                )

                if is_key_exhausted:
                    self._exhausted_keys.add(slot)
                    # All 3 models on this key hit TPD/quota — no point
                    # waiting; move to next key immediately.
                    logger.warning(
                        "APIFallback: %s fully exhausted (all models "
                        "hit TPD/quota). Skipping to next key.",
                        cfg.label,
                    )
                    # Also add all remaining models of this key to tried set
                    # so _get_next_candidate skips them.
                    for m in cfg.models:
                        total_tried.add((slot, m.name))
                    # Do NOT count this toward the attempt budget or delay.
                    continue

                logger.warning(
                    "APIFallback: %s / %s failed (%s). "
                    "Trying next key+model. Attempt %d/%d",
                    cfg.label,
                    model,
                    type(exc).__name__,
                    attempt + 1,
                    max_attempts,
                )

                attempt += 1

                if attempt < max_attempts:
                    time.sleep(self.retry_delay)

        if last_exc is not None:
            raise last_exc

        raise RuntimeError(
            f"All {max_attempts} fallback attempts exhausted "
            f"across {len(self._keys)} keys."
        )

    def _get_next_candidate(
        self,
        tried: set[tuple[int, str]],
        skip_slots: set[int] | None = None,
    ) -> tuple[int | None, str | None]:
        """Return the next untried (slot, model) pair, in strict order."""
        for cfg in self._keys:
            if skip_slots and cfg.slot in skip_slots:
                continue
            for model_cfg in sorted(cfg.models):
                if (cfg.slot, model_cfg.name) not in tried:
                    return cfg.slot, model_cfg.name
        return None, None

    @staticmethod
    def _is_quota_exhausted(error_str: str) -> bool:
        """
        Detect TPD (tokens per day) quota exhaustion errors.

        These indicate the key is fully exhausted for the day — trying
        other models on the same key is pointless.
        """
        return "tokens per day" in error_str or "tpd" in error_str

    def _should_fallback(
        self,
        exc: Exception,
        error_str: str,
    ) -> bool:
        """
        Decide whether the error should trigger a fallback.

        Rules
        -----
        - 413  payload too large → do not retry (input itself too big)
        - 429  rate limit / tokens per day / per minute → retry next model+key
        - 400  model not found / invalid → retry the request
        - 401  unauthorized           → stop (key invalid)
        - 403  model blocked at project level → retry next model+key
              (all keys share the same project, but trying a
              different model name can succeed — e.g. qwen vs gpt-oss)
        - 403  authentication         → stop (key invalid)
        - any other error             → retry next model+key
        """
        status = getattr(exc, "status_code", None)

        if status == 413:
            return False

        if "tokens per day" in error_str:
            return True

        if status == 429:
            return True

        if status == 400 and "model" in error_str:
            return True

        if status == 401:
            return False

        if status == 403:
            # Model blocked at project level — retry a different
            # model, because every key shares the same Groq
            # project. The fallback loop naturally cycles
            # through models for the same key, then moves to
            # the next key. So qwen/... still has a chance.
            model_blocked = (
                "model" in error_str
                and (
                    "blocked" in error_str
                    or "permission" in error_str
                    or "not_found" in error_str
                    or "model_not_found" in error_str
                    or "doesn't exist" in error_str
                    or "decommissioned" in error_str
                )
            )
            if model_blocked:
                return True

            if (
                "authentication" in error_str
                or "unauthorized" in error_str
            ):
                return False

            return True

        if (
            "authentication" in error_str
            or "unauthorized" in error_str
        ):
            return False

        return True


# ---------------------------------------------------------------------------
# Global singleton (lazy-initialised on first use)
# ---------------------------------------------------------------------------

_manager: APIFallbackManager | None = None


def get_fallback_manager() -> APIFallbackManager:
    global _manager
    if _manager is None:
        _manager = APIFallbackManager()
    return _manager


def reset_fallback_manager() -> None:
    """Reset the singleton — useful for tests."""
    global _manager
    _manager = None