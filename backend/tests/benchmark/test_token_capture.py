"""
Unit test cho token capture trong ALOFBenchmarkRunner.
Không gọi Groq — fake LLMService để kiểm tra cơ chế tổng hợp.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from backend.application.services.llm_service import LLMService
from backend.application.services.llm_call_metrics import LLMCallMetrics


def make_fake_llm_service() -> MagicMock:
    """Tạo mock LLMService với call_metrics có thể kiểm soát."""
    svc = MagicMock(spec=LLMService)
    svc.call_metrics = []
    svc.total_input_tokens = 0
    svc.total_output_tokens = 0
    svc.total_tokens = 0
    svc.total_duration = 0.0
    return svc


def test_capture_token_usage_returns_zeros_when_no_service():
    """Nếu LLMService is None, trả về dict rỗng."""
    from backend.benchmark.ALOF.runner import ALOFBenchmarkRunner

    # Patch orchestrator factory before import-time init
    import backend.benchmark.ALOF.runner as runner_module

    runner = ALOFBenchmarkRunner.__new__(
        ALOFBenchmarkRunner,
    )
    runner.adapter = MagicMock()
    runner.orchestrator = MagicMock()
    runner._llm_service = None

    usage = runner._capture_token_usage()

    assert usage == {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "call_count": 0,
        "duration_seconds": 0.0,
        "per_stage": {},
    }


def test_capture_token_usage_sums_per_stage():
    """Nếu LLMService có metrics, group theo stage."""
    from backend.benchmark.ALOF.runner import ALOFBenchmarkRunner

    runner = ALOFBenchmarkRunner.__new__(
        ALOFBenchmarkRunner,
    )
    runner.adapter = MagicMock()
    runner.orchestrator = MagicMock()

    svc = make_fake_llm_service()
    svc.call_metrics = [
        LLMCallMetrics(
            stage="router",
            component="LLMRouter",
            duration=1.0,
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
        ),
        LLMCallMetrics(
            stage="router",
            component="LLMRouter",
            duration=0.5,
            input_tokens=80,
            output_tokens=40,
            total_tokens=120,
        ),
        LLMCallMetrics(
            stage="planner",
            component="SequentialPlanner",
            duration=2.0,
            input_tokens=200,
            output_tokens=100,
            total_tokens=300,
        ),
    ]
    runner._llm_service = svc

    usage = runner._capture_token_usage()

    assert usage["call_count"] == 3
    assert usage["input_tokens"] == 380
    assert usage["output_tokens"] == 190
    assert usage["total_tokens"] == 570
    assert usage["duration_seconds"] == 3.5

    assert "router" in usage["per_stage"]
    assert "planner" in usage["per_stage"]

    router = usage["per_stage"]["router"]
    assert router["call_count"] == 2
    assert router["input_tokens"] == 180
    assert router["output_tokens"] == 90
    assert router["total_tokens"] == 270

    planner = usage["per_stage"]["planner"]
    assert planner["call_count"] == 1
    assert planner["total_tokens"] == 300

    # reset_call_count was called
    svc.reset_call_count.assert_called_once()


def test_run_case_persists_token_usage():
    """run_case phải trả về dict có 'token_usage'."""
    from backend.benchmark.ALOF.runner import ALOFBenchmarkRunner

    runner = ALOFBenchmarkRunner.__new__(
        ALOFBenchmarkRunner,
    )
    runner.adapter = MagicMock()
    runner.orchestrator = MagicMock()

    svc = make_fake_llm_service()
    svc.call_metrics = [
        LLMCallMetrics(
            stage="runtime",
            component="SequentialRuntime",
            duration=1.5,
            input_tokens=150,
            output_tokens=75,
            total_tokens=225,
        ),
    ]
    runner._llm_service = svc

    sample = {
        "case_id": "test_case_001",
        "learner": {"id": "l1", "name": "Alice"},
        "history": [],
    }

    # Stub build_request + orchestrator.execute
    runner.build_request = MagicMock(
        return_value=MagicMock(),
    )

    fake_result = MagicMock()
    fake_result.final_artifact = MagicMock(content="answer")
    fake_result.metadata = {"key": "val"}
    runner.orchestrator.execute.return_value = fake_result

    out = runner.run_case(sample)

    assert out["case_id"] == "test_case_001"
    assert out["prediction"] == "answer"
    assert "token_usage" in out
    assert out["token_usage"]["call_count"] == 1
    assert out["token_usage"]["total_tokens"] == 225
    assert "runtime" in out["token_usage"]["per_stage"]