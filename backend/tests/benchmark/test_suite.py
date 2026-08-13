from __future__ import annotations

from backend.benchmark.experiment import (
    BenchmarkExperiment,
)
from backend.benchmark.scenario import (
    BenchmarkScenario,
)
from backend.benchmark.suite import (
    BenchmarkSuite,
)
from backend.benchmark.result import (
    BenchmarkResult,
)


class FakeBenchmarkExperiment:
    """
    Fake experiment for testing BenchmarkSuite.
    """

    def run_single_agent(
        self,
        scenario: BenchmarkScenario,
    ) -> BenchmarkResult:

        return BenchmarkResult(
            scenario_id=scenario.id,
            approach="single_agent",
            success=True,
            output=(
                f"Single result: {scenario.id}"
            ),
            metadata={
                "duration": 1.0,
                "llm_calls": 1,
            },
        )

    def run_multi_agent(
        self,
        scenario: BenchmarkScenario,
    ) -> BenchmarkResult:

        return BenchmarkResult(
            scenario_id=scenario.id,
            approach="multi_agent",
            success=True,
            output=(
                f"Multi result: {scenario.id}"
            ),
            metadata={
                "duration": 2.0,
                "llm_calls": 2,
            },
        )


def create_scenarios() -> list[BenchmarkScenario]:

    return [
        BenchmarkScenario(
            id="python_explanation",
            name="Python Explanation",
            user_request="Explain Python.",
            component_ids=[
                "research",
                "mentor",
            ],
            expected_output="Lesson",
        ),
        BenchmarkScenario(
            id="python_roadmap",
            name="Python Roadmap",
            user_request=(
                "Create a Python learning roadmap."
            ),
            component_ids=[
                "planner",
            ],
            expected_output="Roadmap",
        ),
    ]


def test_benchmark_suite_runs_multiple_scenarios():

    experiment = FakeBenchmarkExperiment()

    suite = BenchmarkSuite(
        experiment=experiment,
    )

    scenarios = create_scenarios()

    comparisons = suite.run(
        scenarios,
    )

    assert len(
        comparisons,
    ) == 2


def test_benchmark_suite_preserves_scenario_ids():

    experiment = FakeBenchmarkExperiment()

    suite = BenchmarkSuite(
        experiment=experiment,
    )

    comparisons = suite.run(
        create_scenarios(),
    )

    assert [
        comparison.single_agent.scenario_id
        for comparison in comparisons
    ] == [
        "python_explanation",
        "python_roadmap",
    ]


def test_benchmark_suite_contains_both_approaches():

    experiment = FakeBenchmarkExperiment()

    suite = BenchmarkSuite(
        experiment=experiment,
    )

    comparisons = suite.run(
        create_scenarios(),
    )

    for comparison in comparisons:

        assert (
            comparison.single_agent.approach
            == "single_agent"
        )

        assert (
            comparison.multi_agent.approach
            == "multi_agent"
        )


def test_benchmark_suite_keeps_results_independent():

    experiment = FakeBenchmarkExperiment()

    suite = BenchmarkSuite(
        experiment=experiment,
    )

    comparisons = suite.run(
        create_scenarios(),
    )

    assert (
        comparisons[0]
        .single_agent
        .output
        == "Single result: python_explanation"
    )

    assert (
        comparisons[1]
        .single_agent
        .output
        == "Single result: python_roadmap"
    )