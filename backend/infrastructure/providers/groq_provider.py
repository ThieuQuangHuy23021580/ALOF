from __future__ import annotations

import logging
import time

from openai import OpenAI
from openai import RateLimitError

from backend.config import settings

from .llm_provider import LLMProvider


logger = logging.getLogger(__name__)


class GroqProvider(
    LLMProvider,
):
    """
    Groq implementation of LLMProvider.

    Uses the OpenAI-compatible Chat Completions API.
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
        retry_delay = 20.0

        for attempt in range(
            retries,
        ):

            try:

                logger.info(
                    "Groq request: messages=%d chars=%d",
                    len(messages),
                    sum(
                        len(
                            message.get(
                                "content",
                                "",
                            )
                        )
                        for message in messages
                    ),
                )

                response = (
                    self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=settings.temperature,
                        max_completion_tokens=(
                            settings.max_output_tokens
                        ),
                        response_format={
                            "type": "json_object",
                        },
                    )
                )

                # --------------------------------------------------
                # Capture usage from the actual API response.
                # --------------------------------------------------

                usage = response.usage

                if usage is not None:

                    self._last_input_tokens = (
                        getattr(
                            usage,
                            "prompt_tokens",
                            0,
                        )
                        or 0
                    )

                    self._last_output_tokens = (
                        getattr(
                            usage,
                            "completion_tokens",
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

                # --------------------------------------------------
                # Extract final assistant content.
                # --------------------------------------------------

                content = (
                    response.choices[0]
                    .message
                    .content
                ) or ""

                logger.info(
                    "Groq response received: "
                    "input_tokens=%d output_tokens=%d "
                    "total_tokens=%d",
                    self._last_input_tokens,
                    self._last_output_tokens,
                    self._last_total_tokens,
                )

                return content

            except RateLimitError as exc:

                status_code = getattr(
                    exc,
                    "status_code",
                    None,
                )

                error_message = str(
                    exc,
                )

                lower_message = (
                    error_message.lower()
                )

                # --------------------------------------------------
                # Request entity too large.
                #
                # This is not a temporary rate limit.
                # Do not retry.
                # --------------------------------------------------

                if status_code == 413:

                    logger.error(
                        "Groq request rejected: "
                        "request entity too large."
                    )

                    raise

                # --------------------------------------------------
                # Daily token quota exhausted.
                #
                # Retrying immediately will not help.
                # --------------------------------------------------

                if (
                    "tokens per day"
                    in lower_message
                ):

                    logger.error(
                        "Groq request rejected: "
                        "daily token quota exhausted."
                    )

                    raise

                # --------------------------------------------------
                # Temporary TPM rate limit.
                #
                # Retry after a fixed 20 seconds.
                # --------------------------------------------------

                if (
                    status_code == 429
                    and "tokens per minute"
                    in lower_message
                ):

                    if attempt == retries - 1:

                        logger.error(
                            "Groq TPM rate limit persisted "
                            "after %d attempts.",
                            retries,
                        )

                        raise

                    logger.warning(
                        "Groq TPM rate limit reached. "
                        "Retrying attempt %d/%d in %.1fs.",
                        attempt + 1,
                        retries,
                        retry_delay,
                    )

                    time.sleep(
                        retry_delay,
                    )

                    continue

                # --------------------------------------------------
                # Other temporary rate limits.
                # --------------------------------------------------

                if attempt == retries - 1:

                    logger.error(
                        "Groq rate limit persisted "
                        "after %d attempts.",
                        retries,
                    )

                    raise

                logger.warning(
                    "Groq rate limit. "
                    "Retrying attempt %d/%d in %.1fs.",
                    attempt + 1,
                    retries,
                    retry_delay,
                )

                time.sleep(
                    retry_delay,
                )

        raise RuntimeError(
            "Failed to generate response."
        )