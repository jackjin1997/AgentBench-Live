"""CLI entry point for AgentBench-Live."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """AgentBench-Live: The real-time leaderboard for AI agent task execution."""
    pass


@main.command()
@click.option("--agent", required=True, help="Agent to benchmark (e.g. claude-code, openclaw)")
@click.option("--domain", default="all", help="Task domain: code, research, data, tool-use, multi-step, or all")
@click.option("--difficulty", default="all", help="Difficulty: easy, medium, hard, or all")
@click.option("--trials", default=None, type=int, help="Number of trials per task (for pass@k)")
@click.option("--output", default="results", help="Output directory for results")
@click.option("--tasks-dir", default="tasks", help="Tasks directory path")
def run(agent: str, domain: str, difficulty: str, trials: Optional[int], output: str, tasks_dir: str):
    """Run benchmark tasks against an agent."""
    import agentbench.adapters.aider  # noqa: F401
    import agentbench.adapters.claude_code  # noqa: F401
    import agentbench.adapters.codex_cli  # noqa: F401
    import agentbench.adapters.gemini_cli  # noqa: F401
    import agentbench.adapters.openclaw  # noqa: F401
    from agentbench.runner import run_benchmark

    run_benchmark(
        agent_name=agent,
        tasks_dir=Path(tasks_dir),
        domain=domain,
        difficulty=difficulty,
        trials=trials,
        output_dir=Path(output),
    )


@main.command()
@click.option("--results-dir", default="results", help="Results directory")
def leaderboard(results_dir: str):
    """Display current leaderboard rankings."""
    from agentbench.ranking import load_rankings

    rankings = load_rankings(Path(results_dir))

    if not rankings:
        console.print("[yellow]No results found. Run benchmarks first.[/yellow]")
        return

    table = Table(title="AgentBench-Live Leaderboard")
    table.add_column("Rank", justify="right", style="bold")
    table.add_column("Agent", style="cyan")
    table.add_column("Score", justify="right")
    table.add_column("pass@k", justify="right")
    table.add_column("Tasks", justify="right")

    for i, entry in enumerate(rankings, 1):
        table.add_row(
            str(i),
            entry["agent"],
            f"{entry['avg_score']:.2f}",
            f"{entry['pass_rate']:.0%}",
            str(entry["total_tasks"]),
        )

    console.print(table)


@main.command()
@click.option("--tasks-dir", default="tasks", help="Tasks directory path")
@click.option("--domain", default="all", help="Filter by domain")
def tasks(tasks_dir: str, domain: str):
    """List available benchmark tasks."""
    from agentbench.schema import Domain, load_all_tasks

    all_tasks = load_all_tasks(Path(tasks_dir))
    if domain != "all":
        all_tasks = [t for t in all_tasks if t.domain == Domain(domain)]

    table = Table(title=f"Available Tasks ({len(all_tasks)})")
    table.add_column("ID", style="cyan")
    table.add_column("Domain")
    table.add_column("Difficulty")
    table.add_column("Title")
    table.add_column("Time (min)", justify="right")

    for t in all_tasks:
        table.add_row(t.id, t.domain.value, t.difficulty.value, t.title, str(t.human_time_minutes))

    console.print(table)


@main.command()
def agents():
    """List available agent adapters."""
    import agentbench.adapters.aider  # noqa: F401
    import agentbench.adapters.claude_code  # noqa: F401
    import agentbench.adapters.codex_cli  # noqa: F401
    import agentbench.adapters.gemini_cli  # noqa: F401
    import agentbench.adapters.openclaw  # noqa: F401
    from agentbench.adapters import get_adapter, list_adapters

    table = Table(title="Available Agents")
    table.add_column("Name", style="cyan")
    table.add_column("Available", justify="center")

    for name in list_adapters():
        adapter = get_adapter(name)
        available = "YES" if adapter.is_available() else "NO"
        table.add_row(name, available)

    console.print(table)


@main.command("upload-evaluators")
def upload_evaluators():
    """Upload AgentBench evaluators to LangSmith."""
    from agentbench.langsmith_eval import upload_benchmark_evaluators

    upload_benchmark_evaluators()


@main.command("export-dataset")
@click.argument("results_file")
@click.option("--name", default="agentbench-live", help="Dataset name in LangSmith")
def export_dataset(results_file: str, name: str):
    """Export benchmark results as a LangSmith dataset."""
    from agentbench.langsmith_dataset import export_dataset as _export

    _export(Path(results_file), dataset_name=name)


@main.command("social-card")
@click.option("--results", default="leaderboard/data/rankings.json", help="Path to results JSON")
@click.option("--output", default="social-card.png", help="Output PNG file path")
@click.option("--agents", default=None, help="Comma-separated agent slugs to include")
def social_card(results: str, output: str, agents: Optional[str]):
    """Generate a shareable social card image with agent comparisons."""
    from agentbench.social_card import generate_social_card

    agent_list = [a.strip() for a in agents.split(",")] if agents else None
    out = generate_social_card(results, output, agents=agent_list)
    console.print(f"[green]Social card saved to {out}[/green]")


if __name__ == "__main__":
    main()
