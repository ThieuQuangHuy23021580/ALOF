from __future__ import annotations

import pytest

from pydantic import BaseModel

from backend.core.json_parser import JsonParser


class LessonPayload(BaseModel):

    title: str

    content: str

    summary: str


def test_json_parser_parses_valid_json():

    parser = JsonParser(
        LessonPayload,
    )

    raw = """
    {
        "title": "Python Basics",
        "content": "Python is a programming language.",
        "summary": "Introduction to Python."
    }
    """

    result = parser.parse(
        raw,
    )

    assert isinstance(
        result,
        LessonPayload,
    )

    assert result.title == (
        "Python Basics"
    )

    assert result.content == (
        "Python is a programming language."
    )

    assert result.summary == (
        "Introduction to Python."
    )


def test_json_parser_validates_pydantic_schema():

    parser = JsonParser(
        LessonPayload,
    )

    raw = """
    {
        "title": "Python Basics",
        "content": "Python is a programming language.",
        "summary": "Introduction to Python."
    }
    """

    result = parser.parse(
        raw,
    )

    assert result.model_dump() == {
        "title": "Python Basics",
        "content": (
            "Python is a programming language."
        ),
        "summary": (
            "Introduction to Python."
        ),
    }


def test_json_parser_rejects_invalid_json():

    parser = JsonParser(
        LessonPayload,
    )

    raw = """
    {
        "title": "Python Basics",
        "content": "Missing closing brace"
    """

    with pytest.raises(
        ValueError,
        match="Invalid JSON response.",
    ):
        parser.parse(
            raw,
        )


def test_json_parser_rejects_invalid_schema():

    parser = JsonParser(
        LessonPayload,
    )

    raw = """
    {
        "title": "Python Basics",
        "content": "Python is a programming language."
    }
    """

    with pytest.raises(
        ValueError,
        match="Invalid response schema.",
    ):
        parser.parse(
            raw,
        )


def test_json_parser_rejects_wrong_field_type():

    parser = JsonParser(
        LessonPayload,
    )

    raw = """
    {
        "title": 123,
        "content": "Python is a programming language.",
        "summary": "Introduction to Python."
    }
    """

    with pytest.raises(
        ValueError,
        match="Invalid response schema.",
    ):
        parser.parse(
            raw,
        )


def test_json_parser_supports_different_models():

    class QuizPayload(BaseModel):

        question: str

        answer: str

    parser = JsonParser(
        QuizPayload,
    )

    raw = """
    {
        "question": "What is Python?",
        "answer": "A programming language."
    }
    """

    result = parser.parse(
        raw,
    )

    assert isinstance(
        result,
        QuizPayload,
    )

    assert result.question == (
        "What is Python?"
    )

    assert result.answer == (
        "A programming language."
    )

def test_json_parser_rejects_non_object_json():

    parser = JsonParser(
        LessonPayload,
    )

    raw = """
    [
        {
            "title": "Python"
        }
    ]
    """

    with pytest.raises(
        ValueError,
        match="Invalid response schema.",
    ):
        parser.parse(
            raw,
        )