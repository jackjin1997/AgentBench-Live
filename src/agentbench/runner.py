"""Benchmark runner — orchestrates task execution and evaluation."""

from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path

from rich.console import Console
from rich.table import Table

from agentbench.adapters import get_adapter
from agentbench.adapters.base import AgentResult
from agentbench.evaluator import EvalScore, Evaluator
from agentbench.sandbox import Sandbox
from agentbench.schema import Domain, Difficulty, Task, load_all_tasks

console = Console()

# Number of trials per task for pass^k calculation
DEFAULT_TRIALS = 3


def run_benchmark(
    agent_name: str,
    tasks_dir: Path,
    domain: str = "all",
    difficulty: str = "all",
    trials: int = DEFAULT_TRIALS,
    output_dir: Path | None = None,
) -> list[EvalScore]:
    """Run a full benchmark suite against an agent.

    Args:
        agent_name: Name of the agent adapter to use.
        tasks_dir: Path to the tasks directory.
        domain: Filter by domain, or "all".
        difficulty: Filter by difficulty, or "all".
        trials: Number of trials per task (for pass^k).
        output_dir: Directory to save results JSON.

    Returns:
        List of EvalScore for each task.
    """
    adapter = get_adapter(agent_name)

    if not adapter.is_available():
        console.print(f"[red]Agent '{agent_name}' is not available on this system.[/red]")
        return []

    # Load and filter tasks
    all_tasks = load_all_tasks(tasks_dir)
    tasks = _filter_tasks(all_tasks, domain, difficulty)

    if not tasks:
        console.print("[yellow]No tasks match the specified filters.[/yellow]")
        return []

    console.print(f"\n[bold]AgentBench-Live[/bold] — Running {len(tasks)} tasks × {trials} trials against [cyan]{agent_name}[/cyan]\n")

    evaluator = Evaluator()
    all_scores: list[EvalScore] = []

    for task in tasks:
        console.print(f"[bold]{task.id}[/bold] — {task.title} [{task.domain.value}/{task.difficulty.value}]")

        trial_scores: list[EvalScore] = []

        for trial in range(1, trials + 1):
            console.print(f"  Trial {trial}/{trials}...", end=" ")

            with Sandbox(task) as sandbox:
                # Resolve /workspace references to actual tmpdir path
                resolved_prompt = sandbox.resolve_prompt(task.prompt)

                # Run agent
                result = adapter.run(
                    prompt=resolved_prompt,
                    workspace=sandbox.workspace,
                    timeout_seconds=task.evaluation.timeout_seconds,
                    network=task.setup.network,
                )
                result.task_id = task.id

                # Evaluate
                score = evaluator.evaluate(task, result, sandbox)
                trial_scores.append(score)

                status = "[green]PASS[/green]" if score.score >= 0.8 else "[red]FAIL[/red]"
                console.print(f"{status} (score: {score.score:.2f}, time: {result.duration_seconds:.1f}s)")

        # Compute pass^k
        pass_count = sum(1 for s in trial_scores if s.score >= 0.8)
        pass_at_k = pass_count / trials

        # Use best trial score, but record pass^k
        best_score = max(trial_scores, key=lambda s: s.score)
        best_score.pass_at_k = pass_at_k

        console.print(f"  → pass@{trials}: {pass_at_k:.1%} | best: {best_score.score:.2f}\n")
        all_scores.append(best_score)

    # Print summary table
    _print_summary(all_scores, agent_name)

    # Save results
    if output_dir:
        _save_results(all_scores, agent_name, output_dir)

    return all_scores


def _filter_tasks(tasks: list[Task], domain: str, difficulty: str) -> list[Task]:
    filtered = tasks
    if domain != "all":
        filtered = [t for t in filtered if t.domain == Domain(domain)]
    if difficulty != "all":
        filtered = [t for t in filtered if t.difficulty == Difficulty(difficulty)]
    return filtered


def _print_summary(scores: list[EvalScore], agent_name: str):
    table = Table(title=f"Results: {agent_name}")
    table.add_column("Task", style="cyan")
    table.add_column("Score", justify="right")
    table.add_column("pass@k", justify="right")
    table.add_column("Status", justify="center")

    for s in scores:
        status = "✅" if s.score >= 0.8 else "❌"
        pk = f"{s.pass_at_k:.0%}" if s.pass_at_k is not None else "—"
        table.add_row(s.task_id, f"{s.score:.2f}", pk, status)

    avg = sum(s.score for s in scores) / max(len(scores), 1)
    table.add_section()
    table.add_row("[bold]Average[/bold]", f"[bold]{avg:.2f}[/bold]", "", "")

    console.print(table)


def _save_results(scores: list[EvalScore], agent_name: str, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    path = output_dir / f"{agent_name}-{ts}.json"

    data = {
        "agent": agent_name,
        "timestamp": ts,
        "scores": [asdict(s) for s in scores],
        "summary": {
            "total_tasks": len(scores),
            "avg_score": sum(s.score for s in scores) / max(len(scores), 1),
            "pass_rate": sum(1 for s in scores if s.score >= 0.8) / max(len(scores), 1),
        },
    }

    path.write_text(json.dumps(data, indent=2))
    console.print(f"\n[dim]Results saved to {path}[/dim]")
