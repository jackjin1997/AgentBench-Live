"""Evaluation engine for scoring agent task results."""

from agentbench.evaluator.composite import CompositeEvaluator
from agentbench.evaluator.models import EvalScore

# Backward-compatible alias — runner.py and cli.py use `Evaluator`
Evaluator = CompositeEvaluator

__all__ = ["CompositeEvaluator", "EvalScore", "Evaluator"]
