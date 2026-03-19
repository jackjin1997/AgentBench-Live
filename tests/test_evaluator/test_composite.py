"""Tests for composite evaluator."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from agentbench.config import BenchmarkConfig
from agentbench.evaluator.composite import CompositeEvaluator
from agentbench.evaluator.models import EvalScore
from agentbench.schema import EvalType


class TestCompositeEvaluator:
    def setup_method(self):
        self.config = BenchmarkConfig()
        self.evaluator = CompositeEvaluator(config=self.config)

    def test_routes_auto(self, sample_task, sample_result, mock_sandbox):
        with patch.object(self.evaluator._auto, "evaluate") as mock_auto:
            mock_auto.return_value = EvalScore(
                task_id="test-001", agent_name="test-agent",
                score=1.0, details={"auto_pass_rate": 1.0}, auto_passed=True,
            )
            score = self.evaluator.evaluate(sample_task, sample_result, mock_sandbox)
        assert score.score == 1.0
        mock_auto.assert_called_once()

    def test_routes_llm_judge(self, judge_task, sample_result, mock_sandbox):
        with patch.object(self.evaluator._judge, "evaluate") as mock_judge:
            mock_judge.return_value = EvalScore(
                task_id="test-003", agent_name="test-agent",
                score=0.8, details={"Quality": 8.0},
            )
            score = self.evaluator.evaluate(judge_task, sample_result, mock_sandbox)
        assert score.score == 0.8
        mock_judge.assert_called_once()

    def test_composite_combines_scores(self, composite_task, sample_result, mock_sandbox):
        with patch.object(self.evaluator._auto, "evaluate") as mock_auto, \
             patch.object(self.evaluator._judge, "evaluate") as mock_judge:
            mock_auto.return_value = EvalScore(
                task_id="test-002", agent_name="test-agent",
                score=1.0, details={"auto_pass_rate": 1.0}, auto_passed=True,
            )
            mock_judge.return_value = EvalScore(
                task_id="test-002", agent_name="test-agent",
                score=0.5, details={"Quality": 5.0},
            )
            score = self.evaluator.evaluate(composite_task, sample_result, mock_sandbox)

        # 1.0 * 0.6 + 0.5 * 0.4 = 0.8
        assert score.score == pytest.approx(0.8)
        assert score.auto_passed is True

    def test_composite_judge_error_fallback(self, composite_task, sample_result, mock_sandbox):
        """When judge fails, use auto score only."""
        with patch.object(self.evaluator._auto, "evaluate") as mock_auto, \
             patch.object(self.evaluator._judge, "evaluate") as mock_judge:
            mock_auto.return_value = EvalScore(
                task_id="test-002", agent_name="test-agent",
                score=1.0, details={"auto_pass_rate": 1.0}, auto_passed=True,
            )
            mock_judge.return_value = EvalScore(
                task_id="test-002", agent_name="test-agent",
                score=0.0, details={"error": 0.0},
            )
            score = self.evaluator.evaluate(composite_task, sample_result, mock_sandbox)

        assert score.score == 1.0  # auto only

    def test_human_placeholder(self, sample_task, sample_result, mock_sandbox):
        sample_task.evaluation.type = EvalType.HUMAN
        score = self.evaluator.evaluate(sample_task, sample_result, mock_sandbox)
        assert score.score == -1.0
        assert score.details == {"status": "awaiting_human_review"}

    def test_custom_weights(self, composite_task, sample_result, mock_sandbox):
        self.config.eval.auto_weight = 0.3
        self.config.eval.judge_weight = 0.7
        evaluator = CompositeEvaluator(config=self.config)

        with patch.object(evaluator._auto, "evaluate") as mock_auto, \
             patch.object(evaluator._judge, "evaluate") as mock_judge:
            mock_auto.return_value = EvalScore(
                task_id="test-002", agent_name="test-agent",
                score=1.0, details={"auto_pass_rate": 1.0}, auto_passed=True,
            )
            mock_judge.return_value = EvalScore(
                task_id="test-002", agent_name="test-agent",
                score=0.5, details={"Quality": 5.0},
            )
            score = evaluator.evaluate(composite_task, sample_result, mock_sandbox)

        # 1.0 * 0.3 + 0.5 * 0.7 = 0.65
        assert score.score == pytest.approx(0.65)
