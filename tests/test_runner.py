"""Tests for benchmark runner."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentbench.adapters.base import AgentResult
from agentbench.config import BenchmarkConfig
from agentbench.evaluator.models import EvalScore
from agentbench.runner import _filter_tasks, _save_results, run_benchmark
from agentbench.schema import Difficulty, Domain


class TestFilterTasks:
    def test_filter_all(self, sample_task):
        tasks = [sample_task]
        assert _filter_tasks(tasks, "all", "all") == tasks

    def test_filter_by_domain(self, sample_task, judge_task):
        tasks = [sample_task, judge_task]
        result = _filter_tasks(tasks, "code", "all")
        assert len(result) == 1
        assert result[0].domain == Domain.CODE

    def test_filter_by_difficulty(self, sample_task, judge_task):
        tasks = [sample_task, judge_task]
        result = _filter_tasks(tasks, "all", "easy")
        assert len(result) == 1
        assert result[0].difficulty == Difficulty.EASY

    def test_filter_both(self, sample_task, judge_task):
        tasks = [sample_task, judge_task]
        result = _filter_tasks(tasks, "code", "easy")
        assert len(result) == 1
        assert result[0].id == "test-001"

    def test_filter_no_match(self, sample_task):
        result = _filter_tasks([sample_task], "research", "all")
        assert result == []


class TestSaveResults:
    def test_saves_json(self, tmp_path):
        scores = [
            EvalScore(
                task_id="test-001", agent_name="agent",
                score=0.9, details={}, pass_at_k=0.67,
            ),
        ]
        _save_results(scores, "agent", tmp_path)
        files = list(tmp_path.glob("*.json"))
        assert len(files) == 1

        data = json.loads(files[0].read_text())
        assert data["agent"] == "agent"
        assert data["summary"]["total_tasks"] == 1
        assert data["summary"]["avg_score"] == 0.9

    def test_creates_output_dir(self, tmp_path):
        output = tmp_path / "nested" / "results"
        scores = [
            EvalScore(task_id="t", agent_name="a", score=0.5, details={}),
        ]
        _save_results(scores, "agent", output)
        assert output.exists()

    def test_custom_pass_threshold(self, tmp_path):
        scores = [
            EvalScore(task_id="t", agent_name="a", score=0.85, details={}),
        ]
        _save_results(scores, "agent", tmp_path, pass_threshold=0.9)
        data = json.loads(list(tmp_path.glob("*.json"))[0].read_text())
        assert data["summary"]["pass_rate"] == 0.0  # 0.85 < 0.9


class TestRunBenchmark:
    @patch("agentbench.runner.get_adapter")
    @patch("agentbench.runner.load_all_tasks")
    @patch("agentbench.runner.Sandbox")
    def test_agent_not_available(self, mock_sandbox, mock_load, mock_get):
        adapter = MagicMock()
        adapter.is_available.return_value = False
        mock_get.return_value = adapter

        result = run_benchmark("test", Path("tasks"))
        assert result == []

    @patch("agentbench.runner.get_adapter")
    @patch("agentbench.runner.load_all_tasks")
    @patch("agentbench.runner.Sandbox")
    def test_no_matching_tasks(self, mock_sandbox, mock_load, mock_get):
        adapter = MagicMock()
        adapter.is_available.return_value = True
        mock_get.return_value = adapter
        mock_load.return_value = []

        result = run_benchmark("test", Path("tasks"))
        assert result == []

    @patch("agentbench.runner.get_adapter")
    @patch("agentbench.runner.load_all_tasks")
    @patch("agentbench.runner.Sandbox")
    @patch("agentbench.runner.Evaluator")
    def test_full_run(self, mock_eval_cls, mock_sandbox_cls, mock_load, mock_get, sample_task):
        # Setup adapter
        adapter = MagicMock()
        adapter.is_available.return_value = True
        adapter.run.return_value = AgentResult(
            agent_name="test", task_id="", success=True,
            exit_code=0, stdout="ok", stderr="", duration_seconds=1.0,
        )
        mock_get.return_value = adapter

        # Setup tasks
        mock_load.return_value = [sample_task]

        # Setup sandbox
        sandbox_instance = MagicMock()
        sandbox_instance.workspace = Path("/tmp/fake")
        sandbox_instance.resolve_prompt.return_value = "resolved prompt"
        sandbox_instance.__enter__ = MagicMock(return_value=sandbox_instance)
        sandbox_instance.__exit__ = MagicMock(return_value=False)
        mock_sandbox_cls.return_value = sandbox_instance

        # Setup evaluator
        evaluator = MagicMock()
        evaluator.evaluate.return_value = EvalScore(
            task_id="test-001", agent_name="test",
            score=0.9, details={}, auto_passed=True,
        )
        mock_eval_cls.return_value = evaluator

        config = BenchmarkConfig()
        config.default_trials = 1
        result = run_benchmark("test", Path("tasks"), trials=1, config=config)

        assert len(result) == 1
        assert result[0].score == 0.9
        assert result[0].pass_at_k is not None
