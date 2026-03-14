"""CLI entry point for AgentBench-Live."""

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
@click.version_option()
def main():
    """AgentBench-Live: The real-time leaderboard for AI agent task execution."""
    pass


@main.command()
@click.option("--agent", required=True, help="Agent to benchmark (e.g. claude-code, openclaw)")
@click.option("--domain", default="all", help="Task domain: code, research, data, tool-use, multi-step, or all")
@click.option("--difficulty", default="all", help="Difficulty: easy, medium, hard, or all")
@click.option("--trials", default=3, help="Number of trials per task (for pass@k)")
@click.option("--output", default="results", help="Output directory for results")
@click.option("--tasks-dir", default="tasks", help="Tasks directory path")
def run(agent: str, domain: str, difficulty: str, trials: int, output: str, tasks_dir: str):
    """Run benchmark tasks against an agent."""
    # Import here to ensure adapters are registered
    import agentbench.adapters.claude_code  # noqa: F401
    import agentbench.adapters.openclaw  # noqa: F401
    import agentbench.adapters.gemini_cli  # noqa: F401
    import agentbench.adapters.codex_cli  # noqa: F401
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
    import agentbench.adapters.claude_code  # noqa: F401
    import agentbench.adapters.openclaw  # noqa: F401
    import agentbench.adapters.gemini_cli  # noqa: F401
    import agentbench.adapters.codex_cli  # noqa: F401
    from agentbench.adapters import get_adapter, list_adapters

    table = Table(title="Available Agents")
    table.add_column("Name", style="cyan")
    table.add_column("Available", justify="center")

    for name in list_adapters():
        adapter = get_adapter(name)
        available = "✅" if adapter.is_available() else "❌"
        table.add_row(name, available)

    console.print(table)


if __name__ == "__main__":
    main()
