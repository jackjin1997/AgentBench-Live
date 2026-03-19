"""Shared fixtures for AgentBench-Live tests."""

from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from agentbench.adapters.base import AgentResult
from agentbench.config import BenchmarkConfig, EvalSettings
from agentbench.evaluator.models import EvalScore
from agentbench.schema import (
    AutoEvalConfig,
    Difficulty,
    Domain,
    EvalConfig,
    EvalType,
    LLMJudgeConfig,
    SetupConfig,
    Task,
)


@pytest.fixture
def sample_task() -> Task:
    """A basic task for testing."""
    return Task(
        id="test-001",
        version=1,
        domain=Domain.CODE,
        difficulty=Difficulty.EASY,
        title="Test Task",
        description="A simple test task",
        human_time_minutes=5,
        setup=SetupConfig(files=[], install="", network=False),
        prompt="Fix the bug in app.py",
        evaluation=EvalConfig(
            type=EvalType.AUTO,
            auto=AutoEvalConfig(command="pytest tests/", pass_threshold=1.0),
            timeout_seconds=60,
        ),
    )


@pytest.fixture
def composite_task() -> Task:
    """A task with composite evaluation."""
    return Task(
        id="test-002",
        version=1,
        domain=Domain.DATA,
        difficulty=Difficulty.MEDIUM,
        title="Composite Task",
        description="A task with composite evaluation",
        human_time_minutes=10,
        setup=SetupConfig(files=[], install="", network=True),
        prompt="Analyze the data in data.csv",
        evaluation=EvalConfig(
            type=EvalType.COMPOSITE,
            auto=AutoEvalConfig(command="pytest tests/", pass_threshold=1.0),
            llm_judge=LLMJudgeConfig(
                rubric="Accuracy: data analysis quality\nClarity: explanation clarity",
                reference_answer="Expected analysis output",
                model="claude-sonnet-4-6",
            ),
            timeout_seconds=120,
        ),
    )


@pytest.fixture
def judge_task() -> Task:
    """A task with LLM judge evaluation only."""
    return Task(
        id="test-003",
        version=1,
        domain=Domain.RESEARCH,
        difficulty=Difficulty.HARD,
        title="Judge Task",
        description="A task evaluated by LLM judge",
        human_time_minutes=15,
        setup=SetupConfig(files=[], install="", network=True),
        prompt="Write a security audit report",
        evaluation=EvalConfig(
            type=EvalType.LLM_JUDGE,
            llm_judge=LLMJudgeConfig(
                rubric="Thoroughness: coverage\nAccuracy: correctness",
                reference_answer="Reference report content",
                model="claude-sonnet-4-6",
            ),
            timeout_seconds=180,
        ),
    )


@pytest.fixture
def sample_result() -> AgentResult:
    """A basic agent result."""
    return AgentResult(
        agent_name="test-agent",
        task_id="test-001",
        success=True,
        exit_code=0,
        stdout="All tests passed.\n5 passed in 1.2s",
        stderr="",
        duration_seconds=10.5,
    )


@pytest.fixture
def failed_result() -> AgentResult:
    """A failed agent result."""
    return AgentResult(
        agent_name="test-agent",
        task_id="test-001",
        success=False,
        exit_code=1,
        stdout="3 passed, 2 failed in 2.1s",
        stderr="AssertionError: expected True",
        duration_seconds=15.0,
    )


@pytest.fixture
def mock_sandbox(tmp_path):
    """A mock sandbox with a temporary workspace."""
    sandbox = MagicMock()
    sandbox.workspace = tmp_path
    sandbox.run_command.return_value = MagicMock(
        returncode=0, stdout="5 passed in 1.0s", stderr=""
    )
    return sandbox


@pytest.fixture
def config() -> BenchmarkConfig:
    """A default benchmark config."""
    return BenchmarkConfig()


@pytest.fixture
def sample_results_dir(tmp_path) -> Path:
    """Create a temporary results directory with sample data."""
    results = {
        "agent": "test-agent",
        "timestamp": "20260319-120000",
        "scores": [
            {
                "task_id": "test-001",
                "agent_name": "test-agent",
                "score": 0.9,
                "details": {"auto_pass_rate": 0.9},
                "auto_passed": True,
                "judge_narrative": "",
                "pass_at_k": 0.67,
            }
        ],
        "summary": {
            "total_tasks": 1,
            "avg_score": 0.9,
            "pass_rate": 1.0,
        },
    }
    result_file = tmp_path / "test-agent-20260319-120000.json"
    result_file.write_text(json.dumps(results))
    return tmp_path
