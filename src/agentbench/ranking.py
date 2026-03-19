"""Ranking system — aggregates results into leaderboard."""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_rankings(results_dir: Path) -> list[dict]:
    """Load all results and compute aggregate rankings.

    Returns a sorted list of agent summaries (best score first).
    """
    if not results_dir.exists():
        return []

    agent_scores: dict[str, list[dict]] = {}

    for result_file in results_dir.glob("*.json"):
        try:
            data = json.loads(result_file.read_text())
            agent = data["agent"]
            if agent not in agent_scores:
                agent_scores[agent] = []
            agent_scores[agent].append(data["summary"])
        except (json.JSONDecodeError, KeyError) as exc:
            logger.warning("Failed to load result file %s: %s", result_file, exc)
            continue

    rankings = []
    for agent, summaries in agent_scores.items():
        latest = summaries[-1]
        rankings.append({
            "agent": agent,
            "avg_score": latest["avg_score"],
            "pass_rate": latest["pass_rate"],
            "total_tasks": latest["total_tasks"],
            "runs": len(summaries),
        })

    rankings.sort(key=lambda x: x["avg_score"], reverse=True)
    return rankings


def export_leaderboard_json(results_dir: Path, output_path: Path):
    """Export leaderboard data as JSON for the frontend."""
    rankings = load_rankings(results_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps({
        "rankings": rankings,
        "total_agents": len(rankings),
    }, indent=2))
