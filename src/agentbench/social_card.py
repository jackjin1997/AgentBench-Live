"""Social card generator for AgentBench-Live.

Generates shareable PNG images with radar charts comparing agent scores
across domains. Designed for Twitter/Reddit sharing (1200x630).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional, Sequence


# Domain labels for the radar chart (display name -> JSON key)
DOMAIN_LABELS = {
    "Code": "code",
    "Data": "data",
    "Multi-Step": "multi_step",
    "Research": "research",
    "Tool Use": "tool_use",
}

AGENT_COLORS = [
    "#58a6ff",  # blue
    "#f85149",  # red
    "#3fb950",  # green
    "#d29922",  # orange
    "#bc8cff",  # purple
]

BG_COLOR = "#0d1117"
TEXT_COLOR = "#c9d1d9"
GRID_COLOR = "#30363d"


def _load_results(results_path: str | Path) -> dict[str, Any]:
    """Load results JSON file."""
    path = Path(results_path)
    with open(path) as f:
        return json.load(f)


def generate_social_card(
    results_path: str | Path,
    output_path: str | Path,
    agents: Optional[Sequence[str]] = None,
) -> Path:
    """Generate a social card PNG with a radar chart of agent scores.

    Args:
        results_path: Path to the results/rankings JSON file.
        output_path: Path for the output PNG file.
        agents: Optional list of agent slugs to include. If None, all agents shown.

    Returns:
        Path to the generated PNG file.
    """
    import matplotlib

    matplotlib.use("Agg")  # non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np

    data = _load_results(results_path)
    agent_list = data.get("agents", [])

    if not agent_list:
        # Generate a card with "no data" message
        fig, ax = plt.subplots(figsize=(12, 6.3), facecolor=BG_COLOR)
        ax.set_facecolor(BG_COLOR)
        ax.text(
            0.5, 0.5, "No agent data available",
            ha="center", va="center", fontsize=24, color=TEXT_COLOR,
            transform=ax.transAxes,
        )
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        fig.savefig(str(output_path), dpi=100, bbox_inches="tight", facecolor=BG_COLOR)
        plt.close(fig)
        return Path(output_path)

    # Filter agents if requested
    if agents is not None:
        agent_list = [a for a in agent_list if a["slug"] in agents]

    # Prepare radar data
    domain_keys = list(DOMAIN_LABELS.values())
    domain_names = list(DOMAIN_LABELS.keys())
    num_domains = len(domain_keys)

    # Compute angles for radar chart
    angles = np.linspace(0, 2 * np.pi, num_domains, endpoint=False).tolist()
    angles += angles[:1]  # close the polygon

    # Create figure
    fig = plt.figure(figsize=(12, 6.3), facecolor=BG_COLOR)

    # Radar chart axes (left-center area)
    ax_radar = fig.add_axes([0.05, 0.08, 0.55, 0.78], polar=True, facecolor=BG_COLOR)

    # Configure radar chart
    ax_radar.set_theta_offset(np.pi / 2)
    ax_radar.set_theta_direction(-1)
    ax_radar.set_thetagrids(
        np.degrees(angles[:-1]), domain_names,
        fontsize=10, color=TEXT_COLOR,
    )

    # Gridlines and ticks
    ax_radar.set_ylim(0, 1.0)
    ax_radar.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax_radar.set_yticklabels(["0.25", "0.50", "0.75", "1.00"], fontsize=7, color=GRID_COLOR)
    ax_radar.tick_params(colors=GRID_COLOR)
    ax_radar.spines["polar"].set_color(GRID_COLOR)
    for line in ax_radar.yaxis.get_gridlines():
        line.set_color(GRID_COLOR)
        line.set_linewidth(0.5)
    for line in ax_radar.xaxis.get_gridlines():
        line.set_color(GRID_COLOR)
        line.set_linewidth(0.5)

    # Plot each agent
    for i, agent in enumerate(agent_list):
        color = AGENT_COLORS[i % len(AGENT_COLORS)]
        domains = agent.get("domains", {})
        values = [domains.get(k, {}).get("score", 0) for k in domain_keys]
        values += values[:1]  # close polygon

        ax_radar.plot(angles, values, "o-", linewidth=2, color=color, markersize=4)
        ax_radar.fill(angles, values, alpha=0.15, color=color)

    # Title
    fig.text(
        0.5, 0.95, "AgentBench-Live",
        ha="center", va="top", fontsize=22, fontweight="bold", color=TEXT_COLOR,
    )

    # Agent legend / scores on the right side
    legend_x = 0.68
    legend_y_start = 0.78
    line_height = 0.07

    fig.text(
        legend_x, legend_y_start + 0.06, "Agent Scores",
        ha="left", va="top", fontsize=14, fontweight="bold", color=TEXT_COLOR,
    )

    for i, agent in enumerate(agent_list):
        color = AGENT_COLORS[i % len(AGENT_COLORS)]
        y = legend_y_start - i * line_height
        overall = agent.get("overall_score", 0)

        # Color dot
        fig.patches.append(
            plt.Circle(
                (legend_x - 0.01, y - 0.008), 0.008,
                color=color, transform=fig.transFigure, figure=fig,
            )
        )
        # Agent name and score
        fig.text(
            legend_x + 0.01, y, f"{agent['name']}",
            ha="left", va="top", fontsize=12, color=color, fontweight="bold",
        )
        fig.text(
            legend_x + 0.01, y - 0.03, f"Overall: {overall:.1%}",
            ha="left", va="top", fontsize=10, color=TEXT_COLOR,
        )

    # Footer URL
    fig.text(
        0.5, 0.02, "github.com/jackjin1997/AgentBench-Live",
        ha="center", va="bottom", fontsize=9, color=GRID_COLOR,
    )

    fig.savefig(str(output_path), dpi=100, facecolor=BG_COLOR, bbox_inches="tight")
    plt.close(fig)
    return Path(output_path)
