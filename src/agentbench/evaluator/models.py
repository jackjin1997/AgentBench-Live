"""Evaluation score models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CostMetrics:
    """Cost metrics for one agent run.

    All fields optional — adapters that don't expose token usage simply
    leave them None. Aggregation in v0.3 reports min/median/max across
    trials. See docs/methodology.md#cost-and-latency for the full plan.
    """

    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    cost_usd: Optional[float] = None
    # Provider-specific raw fields (passed through without interpretation)
    raw: dict = field(default_factory=dict)


@dataclass
class LatencyMetrics:
    """Wall-clock latency for one agent run."""

    total_seconds: Optional[float] = None
    time_to_first_output_seconds: Optional[float] = None
    # Number of independent agent steps observable from logs/output
    step_count: Optional[int] = None


@dataclass
class EvalScore:
    """Score from evaluating an agent's task result.

    v0.2: score + auto_passed + judge_narrative
    v0.3 adds: cost (CostMetrics) and latency (LatencyMetrics) — both optional
    so existing results files load without migration.
    """

    task_id: str
    agent_name: str
    score: float  # 0-1
    details: dict[str, float]
    auto_passed: bool | None = None
    judge_narrative: str = ""
    pass_at_k: float | None = None
    # v0.3 hooks — kept optional so existing JSON deserializes unchanged
    cost: Optional[CostMetrics] = None
    latency: Optional[LatencyMetrics] = None
