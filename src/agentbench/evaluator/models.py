"""Evaluation score models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EvalScore:
    """Score from evaluating an agent's task result."""

    task_id: str
    agent_name: str
    score: float  # 0-1
    details: dict[str, float]
    auto_passed: bool | None = None
    judge_narrative: str = ""
    pass_at_k: float | None = None
