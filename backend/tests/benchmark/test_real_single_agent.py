from __future__ import annotations

import pytest

from backend.application.services.llm_service import (
    LLMService,
)
from backend.benchmark.experiment import (
    BenchmarkExperiment,
)
from backend.benchmark.scenario import (
    BenchmarkScenario,
)


@pytest.mark.real_llm
def test_real_single_agent_baseline():

    llm = LLMService()

    experiment = BenchmarkExperiment(
        llm=llm,
    )

    scenario = BenchmarkScenario(
        id="python_explanation",
        name="Python Explanation",
        user_request=(
            "Giải thích Python là gì cho một người mới bắt đầu, "
            "bao gồm khái niệm, đặc điểm chính và các ứng dụng cơ bản."
        ),
        component_ids=[
            "mentor",
        ],
        expected_output="Lesson",
    )

    llm.reset_call_count()

    result = experiment.run_single_agent(
        scenario,
    )

    llm_calls = llm.call_count

    assert (
        result.scenario_id
        == "python_explanation"
    )

    assert (
        result.approach
        == "single_agent"
    )

    assert result.success is True

    assert result.output is not None

    assert result.output.strip()

    print(
        "\n===== SINGLE AGENT BASELINE ====="
    )

    print(
        f"Success: {result.success}"
    )

    print(
        f"Duration: "
        f"{result.metadata.get('duration')}"
    )

    print(
        f"LLM calls: "
        f"{llm_calls}"
    )

    print(
        f"Output:\n{result.output}"
    )