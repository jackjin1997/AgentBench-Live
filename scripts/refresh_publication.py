"""Process the latest multi-trial benchmark results into publish-ready data.

Reads all results/{agent}-*.json files, picks the 3 most recent trials per
agent (by mtime), aggregates mean / min / max / median per task and per
domain, and writes:

  - docs/data/rankings.json   (live leaderboard data, multi-trial-aware)
  - docs/findings-fresh.md    (auto-generated update; human reviews + merges into findings.md)

Usage:
  python scripts/refresh_publication.py                # uses default results/ dir
  python scripts/refresh_publication.py --trials 3     # how many recent trials per agent
  python scripts/refresh_publication.py --dry-run      # print without writing
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = REPO_ROOT / "results"
RANKINGS_PATH = REPO_ROOT / "docs" / "data" / "rankings.json"
FRESH_FINDINGS_PATH = REPO_ROOT / "docs" / "findings-fresh.md"

# Display name -> JSON-key (matches existing rankings.json schema)
DOMAIN_DISPLAY = {
    "code": "Code",
    "data": "Data",
    "multi": "Multi-Step",
    "research": "Research",
    "tool": "Tool Use",
}
DOMAIN_KEYS = list(DOMAIN_DISPLAY.keys())  # used for grouping

AGENT_DISPLAY = {
    "claude-code": "Claude Code",
    "gemini-cli": "Gemini CLI",
    "codex-cli": "Codex CLI",
    "aider": "Aider",
}


def domain_of(task_id: str) -> str:
    """code-001 → 'code', multi-001 → 'multi'."""
    return task_id.rsplit("-", 1)[0]


def load_recent_runs(agent: str, trials: int) -> list[dict]:
    """Return up to `trials` most recent runs (by filename timestamp) for the agent."""
    files = sorted(RESULTS_DIR.glob(f"{agent}-*.json"), reverse=True)
    runs: list[dict] = []
    for f in files:
        try:
            d = json.load(open(f))
        except Exception:
            continue
        # Only count "full" runs (≥8 of 10 tasks present), so a partial dev run
        # doesn't pollute the rolling window.
        if len(d.get("scores", [])) >= 8:
            runs.append(d)
        if len(runs) >= trials:
            break
    return runs


def aggregate_agent(agent: str, runs: list[dict]) -> dict:
    """Build a multi-trial aggregate for one agent."""
    if not runs:
        return {}

    # task_id → list of scores across trials
    task_scores: dict[str, list[float]] = defaultdict(list)
    for run in runs:
        for s in run.get("scores", []):
            task_scores[s["task_id"]].append(float(s.get("score", 0)))

    # Per-task stats
    tasks = []
    for tid, scores in sorted(task_scores.items()):
        tasks.append({
            "task_id": tid,
            "trials": len(scores),
            "mean": round(statistics.mean(scores), 3),
            "min": round(min(scores), 3),
            "max": round(max(scores), 3),
            "median": round(statistics.median(scores), 3),
        })

    # Per-domain stats (mean across all trials of all tasks in domain)
    domain_means: dict[str, list[float]] = defaultdict(list)
    for tid, scores in task_scores.items():
        d = domain_of(tid)
        domain_means[d].extend(scores)

    domains = {}
    for d_key in DOMAIN_DISPLAY:
        scores = domain_means.get(d_key, [])
        if scores:
            domains[d_key.replace("multi", "multi_step").replace("tool", "tool_use")] = {
                "score": round(statistics.mean(scores), 3),
                "min": round(min(scores), 3),
                "max": round(max(scores), 3),
                "trial_count": len(scores),
            }

    # Overall = mean of all task scores across all trials
    all_scores = [s for v in task_scores.values() for s in v]
    overall_mean = round(statistics.mean(all_scores), 3) if all_scores else 0
    overall_stdev = round(statistics.stdev(all_scores), 3) if len(all_scores) > 1 else 0

    pass_rate = sum(1 for v in task_scores.values() if statistics.median(v) >= 0.8) / max(len(task_scores), 1)

    return {
        "name": AGENT_DISPLAY.get(agent, agent),
        "slug": agent,
        "overall_score": overall_mean,
        "overall_stdev": overall_stdev,
        "pass_rate": round(pass_rate, 3),
        "trials_per_task": min(len(r.get("scores", [])) for r in runs),
        "trial_count_total": sum(len(r.get("scores", [])) for r in runs),
        "domains": domains,
        "tasks": tasks,
    }


def render_rankings(agents_data: list[dict]) -> dict:
    """Build the rankings.json envelope."""
    # Sort by overall_score
    agents_sorted = sorted(agents_data, key=lambda a: -a["overall_score"])
    for i, a in enumerate(agents_sorted, 1):
        a["rank"] = i

    max_trials = max((a.get("trials_per_task", 0) for a in agents_sorted), default=0)
    from datetime import datetime, timezone
    return {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "benchmark_version": "0.3.0-rc1",
        "tasks_count": 10,
        "trials_per_task": max_trials,
        "trials_observed_max": max_trials,
        "variance_note": (
            "v0.3-rc1 published with multi-trial sweep. Each agent ran the full task suite "
            f"{max_trials} times; reported scores are mean across trials, with min/max in the per-domain breakdown. "
            "See docs/findings.md for the full per-task variance table."
        ),
        "scoring_note": (
            "Code tasks use auto-eval (pytest). Other domains scored by Gemini 2.5 Flash LLM Judge or heuristic "
            "fallback when no judge key is set. Agents run in interactive mode with stdin prompts."
        ),
        "agents": agents_sorted,
    }


def render_fresh_findings(agents_data: list[dict]) -> str:
    """Generate a fresh findings markdown for human review."""
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    lines = [
        f"# Findings (auto-generated · {today})",
        "",
        "> Generated by `scripts/refresh_publication.py` from the latest multi-trial sweep.",
        "> Review and merge into `docs/findings.md`. Don't ship as-is.",
        "",
        "## Overall scores",
        "",
        "| Agent | Mean | Stdev | Trials/task | Pass rate |",
        "|---|---:|---:|---:|---:|",
    ]
    for a in sorted(agents_data, key=lambda x: -x["overall_score"]):
        lines.append(f"| **{a['name']}** | {a['overall_score']:.3f} | ±{a['overall_stdev']:.3f} | {a['trials_per_task']} | {a['pass_rate']:.0%} |")

    lines += ["", "## Per-domain scores (mean across all trials)", ""]
    cols = ["Agent"] + list(DOMAIN_DISPLAY.values())
    lines.append("| " + " | ".join(cols) + " |")
    lines.append("|" + "|".join(["---"] * len(cols)) + "|")
    for a in sorted(agents_data, key=lambda x: -x["overall_score"]):
        row = [f"**{a['name']}**"]
        for d_key in DOMAIN_DISPLAY:
            d_normalized = d_key.replace("multi", "multi_step").replace("tool", "tool_use")
            d = a["domains"].get(d_normalized)
            row.append(f"{d['score']:.2f} ({d['min']:.2f}–{d['max']:.2f})" if d else "—")
        lines.append("| " + " | ".join(row) + " |")

    # Variance hotspots: tasks where any agent's max - min ≥ 0.4
    lines += ["", "## Variance hotspots (max − min ≥ 0.4 within agent)", ""]
    lines.append("| Agent | Task | Min | Max | Spread |")
    lines.append("|---|---|---:|---:|---:|")
    found = False
    for a in agents_data:
        for t in a["tasks"]:
            spread = t["max"] - t["min"]
            if spread >= 0.4:
                found = True
                lines.append(f"| {a['name']} | `{t['task_id']}` | {t['min']:.2f} | {t['max']:.2f} | **{spread:.2f}** |")
    if not found:
        lines.append("| _(none — variance below threshold for all agents)_ | | | | |")

    # Code commodity check
    lines += ["", "## Code commodity check", ""]
    lines.append("| Agent | code-001 mean | code-002 mean | Both perfect? |")
    lines.append("|---|---:|---:|:---:|")
    for a in agents_data:
        c1 = next((t["mean"] for t in a["tasks"] if t["task_id"] == "code-001"), None)
        c2 = next((t["mean"] for t in a["tasks"] if t["task_id"] == "code-002"), None)
        perfect = "✓" if (c1 == 1.0 and c2 == 1.0) else "—"
        lines.append(f"| {a['name']} | {c1:.2f} | {c2:.2f} | {perfect} |" if c1 is not None else f"| {a['name']} | — | — | — |")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=3, help="Recent trials per agent to consider")
    parser.add_argument("--dry-run", action="store_true", help="Print only, no writes")
    parser.add_argument("--agents", nargs="+", default=list(AGENT_DISPLAY.keys()),
                        help="Agents to include (slugs)")
    args = parser.parse_args()

    agents_data: list[dict] = []
    for agent in args.agents:
        runs = load_recent_runs(agent, args.trials)
        if not runs:
            print(f"  · {agent}: no full-suite runs found, skipping")
            continue
        agg = aggregate_agent(agent, runs)
        if agg:
            print(f"  · {agent}: {agg['trials_per_task']} trials × {len(agg['tasks'])} tasks · overall {agg['overall_score']:.3f} ± {agg['overall_stdev']:.3f}")
            agents_data.append(agg)

    if not agents_data:
        print("No usable runs found. Did the benchmark sweep finish?")
        return 1

    rankings = render_rankings(agents_data)
    fresh = render_fresh_findings(agents_data)

    if args.dry_run:
        print("\n--- rankings.json ---")
        print(json.dumps(rankings, indent=2)[:1500])
        print("...")
        print("\n--- findings-fresh.md (first 1000 chars) ---")
        print(fresh[:1000])
        print("...")
        return 0

    RANKINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RANKINGS_PATH.write_text(json.dumps(rankings, indent=2) + "\n")
    FRESH_FINDINGS_PATH.write_text(fresh)
    print(f"\n✓ wrote {RANKINGS_PATH.relative_to(REPO_ROOT)} ({len(json.dumps(rankings))} bytes)")
    print(f"✓ wrote {FRESH_FINDINGS_PATH.relative_to(REPO_ROOT)} ({len(fresh)} bytes)")
    print(f"\nNext: review {FRESH_FINDINGS_PATH.relative_to(REPO_ROOT)} and merge into findings.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
