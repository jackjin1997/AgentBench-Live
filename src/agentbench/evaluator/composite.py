"""Composite evaluator — combines auto + LLM judge scores."""

from __future__ import annotations

import logging

from agentbench.adapters.base import AgentResult
from agentbench.config import BenchmarkConfig, load_config
from agentbench.evaluator.auto_evaluator import AutoEvaluator
from agentbench.evaluator.judge_evaluator import LLMJudgeEvaluator
from agentbench.evaluator.models import EvalScore
from agentbench.sandbox import Sandbox
from agentbench.schema import EvalType, Task

logger = logging.getLogger(__name__)


class CompositeEvaluator:
    """Orchestrates auto + judge evaluation and combines scores."""

    def __init__(self, config: BenchmarkConfig | None = None):
        self._config = config or load_config()
        self._auto = AutoEvaluator()
        self._judge = LLMJudgeEvaluator(self._config)

    def evaluate(self, task: Task, result: AgentResult, sandbox: Sandbox) -> EvalScore:
        eval_type = task.evaluation.type

        if eval_type == EvalType.AUTO:
            return self._auto.evaluate(task, result, sandbox)
        elif eval_type == EvalType.LLM_JUDGE:
            return self._judge.evaluate(task, result, sandbox)
        elif eval_type == EvalType.COMPOSITE:
            return self._eval_composite(task, result, sandbox)
        else:
            return self._eval_human_placeholder(task, result)

    def _eval_composite(self, task: Task, result: AgentResult, sandbox: Sandbox) -> EvalScore:
        auto_score = self._auto.evaluate(task, result, sandbox)
        judge_score = self._judge.evaluate(task, result, sandbox)

        auto_w = self._config.eval.auto_weight
        judge_w = self._config.eval.judge_weight

        judge_available = "error" not in judge_score.details
        if judge_available:
            combined = auto_score.score * auto_w + judge_score.score * judge_w
        else:
            combined = auto_score.score

        details = {**auto_score.details, **judge_score.details}
        details["auto_weight"] = auto_w
        details["judge_weight"] = judge_w

        return EvalScore(
            task_id=task.id,
            agent_name=result.agent_name,
            score=combined,
            details=details,
            auto_passed=auto_score.auto_passed,
            judge_narrative=judge_score.judge_narrative,
        )

    @staticmethod
    def _eval_human_placeholder(task: Task, result: AgentResult) -> EvalScore:
        return EvalScore(
            task_id=task.id,
            agent_name=result.agent_name,
            score=-1.0,
            details={"status": "awaiting_human_review"},
        )
