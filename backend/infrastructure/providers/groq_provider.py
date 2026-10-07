from __future__ import annotations

import logging

from openai import OpenAI

from backend.config import settings
from backend.infrastructure.providers.api_fallback_manager import (
    get_fallback_manager,
)

from .llm_provider import LLMProvider


logger = logging.getLogger(__name__)


class GroqProvider(
    LLMProvider,
):
    """
    Groq implementation of LLMProvider with automatic API key + model fallback.

    Uses APIFallbackManager to:
    1. Sequentially try each configured API key (in declared order) when
       quota is hit
    2. For each key, try up to 3 models (gpt-oss-120b → gpt-oss-20b →
       qwen/qwen3.8-27b by default)
    3. Sleep ``retry_delay`` seconds between retry attempts

    Fallback is transparent to callers — generate() signature is unchanged.
    """

    def __init__(
        self,
    ) -> None:

        self._fallback = get_fallback_manager()

        self._active_slot: int = 0
        self._active_label: str = ""
        self._active_model: str = ""

        self._last_input_tokens = 0
        self._last_output_tokens = 0
        self._last_total_tokens = 0

    # ======================================================
    # Token usage
    # ======================================================

    @property
    def last_input_tokens(
        self,
    ) -> int:
        return self._last_input_tokens

    @property
    def last_output_tokens(
        self,
    ) -> int:
        return self._last_output_tokens

    @property
    def last_total_tokens(
        self,
    ) -> int:
        return self._last_total_tokens

    # ======================================================
    # Generation
    # ======================================================

    def generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:

        total_chars = sum(
            len(message.get("content", ""))
            for message in messages
        )

        logger.info(
            "Groq request: messages=%d chars=%d",
            len(messages),
            total_chars,
        )

        def call_fn(client_kwargs: dict) -> str:
            client = OpenAI(
                api_key=client_kwargs["api_key"],
                base_url=client_kwargs["base_url"],
            )
            response = client.chat.completions.create(
                model=client_kwargs["model"],
                messages=messages,
                temperature=settings.temperature,
                max_completion_tokens=settings.max_output_tokens,
                response_format={"type": "json_object"},
            )
            return response

        try:
            (
                result,
                slot,
                model,
            ) = self._fallback.execute_with_fallback(
                call_fn,
            )
            self._active_slot = slot
            self._active_model = model

            cfg = next(
                k for k in self._fallback.keys
                if k.slot == slot
            )
            self._active_label = cfg.label

            usage = result.usage

            if usage is not None:
                self._last_input_tokens = (
                    getattr(usage, "prompt_tokens", 0) or 0
                )
                self._last_output_tokens = (
                    getattr(usage, "completion_tokens", 0) or 0
                )
                self._last_total_tokens = (
                    getattr(usage, "total_tokens", 0)
                    or self._last_input_tokens
                    + self._last_output_tokens
                )
            else:
                self._last_input_tokens = 0
                self._last_output_tokens = 0
                self._last_total_tokens = 0

            content = (
                result.choices[0].message.content
            ) or ""

            logger.info(
                "Groq response: %s (slot=%d) model=%s "
                "input_tokens=%d output_tokens=%d total_tokens=%d",
                cfg.label,
                slot,
                model,
                self._last_input_tokens,
                self._last_output_tokens,
                self._last_total_tokens,
            )

            return content

        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Groq all keys+models exhausted after fallback. "
                "Last error: %s",
                exc,
            )
            raise