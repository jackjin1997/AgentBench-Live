"""Tests for auto evaluator."""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from agentbench.evaluator.auto_evaluator import AutoEvaluator
from agentbench.schema import AutoEvalConfig, EvalConfig, EvalType


class TestAutoEvaluator:
    def setup_method(self):
        self.evaluator = AutoEvaluator()

    def test_no_auto_config(self, sample_task, sample_result, mock_sandbox):
        sample_task.evaluation.auto = None
        score = self.evaluator.evaluate(sample_task, sample_result, mock_sandbox)
        assert score.score == 0.0
        assert score.auto_passed is False

    def test_passing_tests(self, sample_task, sample_result, mock_sandbox):
        mock_sandbox.run_command.return_value = MagicMock(
            returncode=0, stdout="5 passed in 1.0s", stderr=""
        )
        score = self.evaluator.evaluate(sample_task, sample_result, mock_sandbox)
        assert score.score == 1.0
        assert score.auto_passed is True

    def test_failing_tests_with_partial_pass(self, sample_task, sample_result, mock_sandbox):
        mock_sandbox.run_command.return_value = MagicMock(
            returncode=1, stdout="3 passed, 2 failed in 2.0s", stderr=""
        )
        score = self.evaluator.evaluate(sample_task, sample_result, mock_sandbox)
        assert score.score == 0.6  # 3/5
        assert score.auto_passed is False

    def test_timeout(self, sample_task, sample_result, mock_sandbox):
        mock_sandbox.run_command.side_effect = subprocess.TimeoutExpired(
            cmd="pytest", timeout=60
        )
        score = self.evaluator.evaluate(sample_task, sample_result, mock_sandbox)
        assert score.score == 0.0
        assert score.auto_passed is False

    def test_os_error(self, sample_task, sample_result, mock_sandbox):
        mock_sandbox.run_command.side_effect = OSError("Command not found")
        score = self.evaluator.evaluate(sample_task, sample_result, mock_sandbox)
        assert score.score == 0.0
        assert score.auto_passed is False


class TestParsePassRate:
    def test_all_passed(self):
        assert AutoEvaluator._parse_pass_rate("10 passed in 3.2s") == 1.0

    def test_mixed_results(self):
        assert AutoEvaluator._parse_pass_rate("3 passed, 2 failed in 2.0s") == 0.6

    def test_no_match(self):
        assert AutoEvaluator._parse_pass_rate("error: no tests found") == 0.0

    def test_empty_string(self):
        assert AutoEvaluator._parse_pass_rate("") == 0.0

    def test_only_passed_no_failed(self):
        assert AutoEvaluator._parse_pass_rate("1 passed in 0.5s") == 1.0
