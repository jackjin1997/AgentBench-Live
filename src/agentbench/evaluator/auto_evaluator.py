"""Auto evaluator — runs test commands and parses results."""

from __future__ import annotations

import logging
import re
import subprocess

from agentbench.adapters.base import AgentResult
from agentbench.evaluator.models import EvalScore
from agentbench.sandbox import Sandbox
from agentbench.schema import Task

logger = logging.getLogger(__name__)


class AutoEvaluator:
    """Evaluates by running automated test commands."""

    def evaluate(self, task: Task, result: AgentResult, sandbox: Sandbox) -> EvalScore:
        auto_cfg = task.evaluation.auto
        if not auto_cfg:
            return EvalScore(
                task_id=task.id, agent_name=result.agent_name,
                score=0.0, details={}, auto_passed=False,
            )

        try:
            test_result = sandbox.run_command(
                auto_cfg.command,
                timeout=task.evaluation.timeout_seconds,
            )
            passed = test_result.returncode == 0
            score = 1.0 if passed else self._parse_pass_rate(test_result.stdout)
        except subprocess.TimeoutExpired:
            logger.warning("Auto eval timed out for task %s", task.id)
            passed = False
            score = 0.0
        except OSError as exc:
            logger.error("Auto eval command failed for task %s: %s", task.id, exc)
            passed = False
            score = 0.0

        return EvalScore(
            task_id=task.id,
            agent_name=result.agent_name,
            score=score,
            details={"auto_pass_rate": score},
            auto_passed=passed,
        )

    @staticmethod
    def _parse_pass_rate(pytest_output: str) -> float:
        """Parse pytest output to extract pass rate."""
        total_match = re.search(r"(\d+) passed(?:.*?(\d+) failed)?", pytest_output)
        if total_match:
            passed = int(total_match.group(1))
            failed = int(total_match.group(2) or 0)
            total = passed + failed
            return passed / total if total > 0 else 0.0
        return 0.0
