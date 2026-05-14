"""Launch-day social card generator.

Generates a 1200x630 PNG (Twitter card / OG image dimensions) that conveys
the v0.2 反共识 narrative:

  1. Same agent, same task, two trials → 0.0 / 0.7 (the variance hook)
  2. "Tied overall" hides 7× per-axis gaps (Tool Use)
  3. Code tasks are commodity (both perfect)

Standalone — does NOT touch src/agentbench/social_card.py to avoid breaking
the CLI command and existing tests.

Usage:
  python scripts/gen_launch_card.py
"""
from __future__ import annotations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ---- Design tokens ----
W_PX, H_PX = 1200, 630
DPI = 100
W, H = W_PX / DPI, H_PX / DPI  # in inches

# Match the leaderboard dark theme
BG = "#0d1117"
PANEL = "#161b22"
LINE = "#30363d"
FG = "#e6edf3"
MUTED = "#8b949e"
ACCENT = "#58a6ff"
RED = "#f85149"
GREEN = "#3fb950"
YELLOW = "#d29922"

OUT = Path(__file__).resolve().parent.parent / "docs" / "social-card-v2.png"


def render() -> Path:
    fig = plt.figure(figsize=(W, H), facecolor=BG, dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W_PX)
    ax.set_ylim(0, H_PX)
    ax.axis("off")

    # ---- Header ----
    ax.text(
        60, H_PX - 50, "AgentBench-Live",
        fontsize=20, color=FG, fontweight="bold", va="top",
    )
    ax.text(
        60, H_PX - 78, "open · MIT · github.com/jackjin1997/AgentBench-Live",
        fontsize=10, color=MUTED, va="top", family="monospace",
    )

    # v0.2 pill (top right)
    pill = patches.FancyBboxPatch(
        (W_PX - 130, H_PX - 65), 80, 28,
        boxstyle="round,pad=0,rounding_size=14",
        facecolor=PANEL, edgecolor=LINE, linewidth=1,
    )
    ax.add_patch(pill)
    ax.text(
        W_PX - 90, H_PX - 51, "v0.2",
        fontsize=10, color=ACCENT, fontweight="bold", ha="center", va="center",
        family="monospace",
    )

    # ---- Main hook (giant) ----
    # Line 1 — context label
    ax.text(
        60, H_PX - 130, "Same agent. Same task. Two trials.",
        fontsize=22, color=MUTED, va="top",
    )

    # Two number groups, stacked label-on-top so big numbers can breathe.
    group1_x = 130
    group2_x = 600
    arrow_x = (group1_x + group2_x) / 2 + 90
    label_y = H_PX - 165
    num_y = H_PX - 290  # baseline for the big numbers

    # Trial 1
    ax.text(group1_x, label_y, "TRIAL 1", fontsize=15, color=MUTED,
            fontweight="bold", va="top", family="monospace", ha="center")
    ax.text(group1_x, num_y, "0.0", fontsize=80, color=RED,
            fontweight="bold", va="bottom", ha="center")

    # Arrow
    ax.text(arrow_x, num_y - 40, "→", fontsize=50, color=MUTED, va="bottom", ha="center")

    # Trial 2
    ax.text(group2_x, label_y, "TRIAL 2", fontsize=15, color=MUTED,
            fontweight="bold", va="top", family="monospace", ha="center")
    ax.text(group2_x, num_y, "0.7", fontsize=80, color=GREEN,
            fontweight="bold", va="bottom", ha="center")

    # Subtitle below big numbers
    ax.text(60, num_y - 30,
            "Most AI agent leaderboards report a single number.",
            fontsize=14, color=FG, va="top")
    ax.text(60, num_y - 55,
            "We don't think that's honest. This one shows variance.",
            fontsize=14, color=FG, va="top")

    # ---- Lower panel: per-axis gaps ----
    panel_top = 250
    panel_bot = 80
    panel_h = panel_top - panel_bot
    panel_left = 60
    panel_right = W_PX - 60

    # Background panel
    panel = patches.FancyBboxPatch(
        (panel_left, panel_bot), panel_right - panel_left, panel_h,
        boxstyle="round,pad=0,rounding_size=8",
        facecolor=PANEL, edgecolor=LINE, linewidth=1,
    )
    ax.add_patch(panel)

    # Title
    ax.text(
        panel_left + 24, panel_top - 24, "Per-axis gaps that \"tied overall\" hides",
        fontsize=14, color=FG, fontweight="bold", va="top",
    )

    # Bar rows
    # Row data: (label, claude_score, gemini_score, gap_text, gap_color)
    rows = [
        ("Tool Use", 0.35, 0.05, "7×", RED),
        ("Research", 0.70, 0.45, "1.6×", YELLOW),
        ("Code", 1.00, 1.00, "tie", MUTED),
    ]

    # Layout: domain | bar | gap-multiplier | C / G scores
    row_top = panel_top - 60
    row_h = 36
    label_x = panel_left + 24
    bar_left = panel_left + 130
    bar_right = panel_right - 260
    bar_w = bar_right - bar_left
    gap_x = panel_right - 230
    score_x = panel_right - 24

    for i, (label, c, g, gap_text, gap_color) in enumerate(rows):
        y = row_top - i * row_h - 16

        # Domain label
        ax.text(label_x, y, label, fontsize=13, color=FG, va="center", fontweight="bold")

        # Background bar
        ax.add_patch(patches.Rectangle(
            (bar_left, y - 8), bar_w, 16,
            facecolor=BG, edgecolor=LINE, linewidth=0.5,
        ))
        # Claude bar (blue, behind, full width of its score)
        ax.add_patch(patches.Rectangle(
            (bar_left, y - 8), bar_w * c, 16,
            facecolor=ACCENT, alpha=0.9,
        ))
        # Gemini bar (yellow, in front, narrower for high-gap rows)
        ax.add_patch(patches.Rectangle(
            (bar_left, y - 8), bar_w * g, 16,
            facecolor=YELLOW, alpha=0.65,
        ))

        # Gap multiplier (left-aligned column)
        ax.text(gap_x, y, gap_text, fontsize=14, color=gap_color, fontweight="bold", va="center")

        # Per-agent scores, right-aligned
        ax.text(
            score_x, y, f"C {c:.2f}  ·  G {g:.2f}",
            fontsize=11, color=MUTED, va="center", ha="right", family="monospace",
        )

    # ---- Footer ----
    ax.text(
        60, 38, "github.com/jackjin1997/AgentBench-Live",
        fontsize=11, color=ACCENT, va="center", family="monospace",
    )
    ax.text(
        W_PX - 60, 38, "Claude Code  vs  Gemini CLI  ·  10 tasks  ·  Docker sandbox",
        fontsize=10, color=MUTED, va="center", ha="right",
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(OUT), dpi=DPI, facecolor=BG)
    plt.close(fig)
    return OUT


if __name__ == "__main__":
    p = render()
    print(f"Wrote {p} ({p.stat().st_size // 1024} KB)")
