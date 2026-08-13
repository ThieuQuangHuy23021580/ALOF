from __future__ import annotations

import time

from openai import OpenAI
from openai import RateLimitError

from backend.config import settings

from .llm_provider import LLMProvider


class GroqProvider(
    LLMProvider,
):
    """
    Groq implementation of LLMProvider.

    Uses the OpenAI-compatible Responses API.
    """

    def __init__(
        self,
    ) -> None:

        self.client = OpenAI(
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
        )

        self.model = settings.model_name

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

        retries = 3
        delay = 1.0

        for attempt in range(
            retries,
        ):

            try:

                response = self.client.responses.create(
                    model=self.model,
                    input=messages,
                    temperature=settings.temperature,
                    max_output_tokens=settings.max_output_tokens,
                )

                # --------------------------------------------------
                # Capture usage from the actual API response.
                # --------------------------------------------------

                usage = response.usage

                if usage is not None:

                    self._last_input_tokens = (
                        getattr(
                            usage,
                            "input_tokens",
                            0,
                        )
                        or 0
                    )

                    self._last_output_tokens = (
                        getattr(
                            usage,
                            "output_tokens",
                            0,
                        )
                        or 0
                    )

                    self._last_total_tokens = (
                        getattr(
                            usage,
                            "total_tokens",
                            0,
                        )
                        or (
                            self._last_input_tokens
                            + self._last_output_tokens
                        )
                    )

                else:

                    self._last_input_tokens = 0
                    self._last_output_tokens = 0
                    self._last_total_tokens = 0

                return response.output_text

            except RateLimitError:

                if attempt == retries - 1:
                    raise

                print(
                    f"[Groq] Rate limit exceeded. "
                    f"Retrying in {delay:.1f}s..."
                )

                time.sleep(
                    delay,
                )

                delay *= 2

        raise RuntimeError(
            "Failed to generate response."
        )