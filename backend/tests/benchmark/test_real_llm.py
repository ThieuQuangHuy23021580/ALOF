from __future__ import annotations

import pytest

from backend.application.services.llm_service import (
    LLMService,
)
from backend.config import settings


@pytest.mark.real_llm
def test_real_groq_llm():

    if not settings.groq_api_key:
        pytest.skip(
            "Groq API key is not configured."
        )

    llm = LLMService()

    response = llm.generate(
        [
            {
                "role": "user",
                "content": "Trả lời đúng một câu: Python là gì?",
            }
        ],
    )

    assert isinstance(
        response,
        str,
    )

    assert response.strip()