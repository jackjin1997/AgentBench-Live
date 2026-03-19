"""LangSmith evaluator integration — converts AgentBench scores to LangSmith format."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def agentbench_evaluator(run: Any, example: Any) -> dict:
    """LangSmith-compatible evaluator that wraps AgentBench scoring.

    This evaluator extracts the AgentBench score from the run output
    and returns it in LangSmith's expected format.

    Args:
        run: LangSmith Run object with outputs containing 'score' and 'details'.
        example: LangSmith Example object (unused, required by interface).

    Returns:
        Dict with 'score' and 'reasoning' keys.
    """
    outputs = getattr(run, "outputs", {}) or {}
    score = outputs.get("score", 0.0)
    details = outputs.get("details", {})

    return {
        "score": score,
        "reasoning": f"AgentBench evaluation: {details}",
    }


def upload_benchmark_evaluators() -> None:
    """Upload AgentBench evaluators to LangSmith.

    Requires langsmith to be installed and configured.
    """
    try:
        from langsmith import Client
    except ImportError:
        logger.error("langsmith package not installed. Run: pip install langsmith")
        return

    client = Client()
    # Register the evaluator function
    logger.info("Registering AgentBench evaluators with LangSmith")

    # LangSmith evaluators are typically used inline, but we can
    # create a dataset-level evaluator for reuse
    print(
        "AgentBench evaluators are ready for use with LangSmith.\n"
        "Use agentbench.langsmith_eval.agentbench_evaluator as your evaluator function."
    )
