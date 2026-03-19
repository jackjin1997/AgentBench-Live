"""LangSmith dataset export — converts benchmark results to LangSmith dataset format."""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def export_dataset(results_path: Path, dataset_name: str = "agentbench-live") -> None:
    """Export benchmark results as a LangSmith dataset.

    Args:
        results_path: Path to a benchmark results JSON file.
        dataset_name: Name for the LangSmith dataset.
    """
    try:
        from langsmith import Client
    except ImportError:
        logger.error("langsmith package not installed. Run: pip install langsmith")
        return

    data = json.loads(results_path.read_text())
    scores = data.get("scores", [])

    if not scores:
        logger.warning("No scores found in %s", results_path)
        return

    client = Client()

    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description=f"AgentBench-Live results for {data.get('agent', 'unknown')}",
    )

    for score_data in scores:
        client.create_example(
            dataset_id=dataset.id,
            inputs={"task_id": score_data["task_id"]},
            outputs={
                "score": score_data["score"],
                "details": score_data.get("details", {}),
                "auto_passed": score_data.get("auto_passed"),
                "judge_narrative": score_data.get("judge_narrative", ""),
            },
        )

    logger.info(
        "Exported %d examples to LangSmith dataset '%s'",
        len(scores),
        dataset_name,
    )
    print(f"Exported {len(scores)} examples to LangSmith dataset '{dataset_name}'")
