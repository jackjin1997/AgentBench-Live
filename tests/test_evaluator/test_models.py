"""Tests for evaluation score models."""

from agentbench.evaluator.models import EvalScore


class TestEvalScore:
    def test_creation(self):
        score = EvalScore(
            task_id="test-001",
            agent_name="test-agent",
            score=0.85,
            details={"auto_pass_rate": 0.85},
        )
        assert score.task_id == "test-001"
        assert score.score == 0.85

    def test_defaults(self):
        score = EvalScore(
            task_id="t", agent_name="a", score=0.5, details={}
        )
        assert score.auto_passed is None
        assert score.judge_narrative == ""
        assert score.pass_at_k is None

    def test_mutable_pass_at_k(self):
        score = EvalScore(
            task_id="t", agent_name="a", score=0.9, details={}
        )
        score.pass_at_k = 0.67
        assert score.pass_at_k == 0.67
