from __future__ import annotations

from backend.benchmark.scenario import (
    BenchmarkScenario,
)


def test_benchmark_scenario_creation():

    scenario = BenchmarkScenario(
        id="research_to_mentor",
        name="Research to Mentor",
        user_request="Explain Python based on research.",
        component_ids=[
            "research",
            "mentor",
        ],
        expected_output="lesson",
    )

    assert (
        scenario.id
        == "research_to_mentor"
    )

    assert (
        scenario.name
        == "Research to Mentor"
    )

    assert (
        scenario.user_request
        == "Explain Python based on research."
    )

    assert scenario.component_ids == [
        "research",
        "mentor",
    ]

    assert (
        scenario.expected_output
        == "lesson"
    )


def test_benchmark_scenario_defaults():

    scenario = BenchmarkScenario(
        id="single_mentor",
        name="Single Mentor",
        user_request="Explain Python.",
        expected_output="lesson",
    )

    assert scenario.component_ids == []

    assert scenario.metadata == {}


def test_benchmark_scenario_supports_metadata():

    scenario = BenchmarkScenario(
        id="research_to_mentor",
        name="Research to Mentor",
        user_request="Explain Python based on research.",
        component_ids=[
            "research",
            "mentor",
        ],
        expected_output="lesson",
        metadata={
            "category": "multi_agent",
            "difficulty": "medium",
        },
    )

    assert (
        scenario.metadata["category"]
        == "multi_agent"
    )

    assert (
        scenario.metadata["difficulty"]
        == "medium"
    )