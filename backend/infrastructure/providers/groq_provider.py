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
    """


    def __init__(
        self,
    ) -> None:

        self.client = OpenAI(
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
        )

        self.model = settings.model_name


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