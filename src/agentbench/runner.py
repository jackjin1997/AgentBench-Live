"""Benchmark runner — orchestrates task execution and evaluation."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict
from pathlib import Path

from rich.console import Console
from rich.table import Table

from agentbench.adapters import get_adapter
from agentbench.config import BenchmarkConfig, load_config
from agentbench.evaluator import EvalScore, Evaluator
from agentbench.sandbox import Sandbox
from agentbench.schema import Difficulty, Domain, Task, load_all_tasks

logger = logging.getLogger(__name__)
console = Console()


def run_benchmark(
    agent_name: str,
    tasks_dir: Path,
    domain: str = "all",
    difficulty: str = "all",
    trials: int | None = None,
    output_dir: Path | None = None,
    config: BenchmarkConfig | None = None,
) -> list[EvalScore]:
    """Run a full benchmark suite against an agent."""
    cfg = config or load_config()
    if trials is None:
        trials = cfg.default_trials

    adapter = get_adapter(agent_name)

    if not adapter.is_available():
        console.print(f"[red]Agent '{agent_name}' is not available on this system.[/red]")
        return []

    all_tasks = load_all_tasks(tasks_dir)
    tasks = _filter_tasks(all_tasks, domain, difficulty)

    if not tasks:
        console.print("[yellow]No tasks match the specified filters.[/yellow]")
        return []

    console.print(
        f"\n[bold]AgentBench-Live[/bold] — Running {len(tasks)} tasks "
        f"× {trials} trials against [cyan]{agent_name}[/cyan]\n"
    )

    evaluator = Evaluator(config=cfg)
    all_scores: list[EvalScore] = []

    for task in tasks:
        logger.info("Starting task %s (%s/%s)", task.id, task.domain.value, task.difficulty.value)
        console.print(
            f"[bold]{task.id}[/bold] — {task.title} "
            f"[{task.domain.value}/{task.difficulty.value}]"
        )

        trial_scores: list[EvalScore] = []

        for trial in range(1, trials + 1):
            console.print(f"  Trial {trial}/{trials}...", end=" ")

            with Sandbox(task, install_timeout=cfg.install_timeout) as sandbox:
                resolved_prompt = sandbox.resolve_prompt(task.prompt)

                result = adapter.run(
                    prompt=resolved_prompt,
                    workspace=sandbox.workspace,
                    timeout_seconds=task.evaluation.timeout_seconds,
                    network=task.setup.network,
                )
                result.task_id = task.id

                score = evaluator.evaluate(task, result, sandbox)
                trial_scores.append(score)

                passed = score.score >= cfg.eval.pass_threshold
                status = "[green]PASS[/green]" if passed else "[red]FAIL[/red]"
                console.print(
                    f"{status} (score: {score.score:.2f}, "
                    f"time: {result.duration_seconds:.1f}s)"
                )

        pass_count = sum(
            1 for s in trial_scores if s.score >= cfg.eval.pass_threshold
        )
        pass_at_k = pass_count / trials

        best_score = max(trial_scores, key=lambda s: s.score)
        best_score.pass_at_k = pass_at_k

        console.print(f"  → pass@{trials}: {pass_at_k:.1%} | best: {best_score.score:.2f}\n")
        all_scores.append(best_score)

    _print_summary(all_scores, agent_name, cfg.eval.pass_threshold)

    if output_dir:
        _save_results(all_scores, agent_name, output_dir, cfg.eval.pass_threshold)

    return all_scores


def _filter_tasks(tasks: list[Task], domain: str, difficulty: str) -> list[Task]:
    filtered = tasks
    if domain != "all":
        filtered = [t for t in filtered if t.domain == Domain(domain)]
    if difficulty != "all":
        filtered = [t for t in filtered if t.difficulty == Difficulty(difficulty)]
    return filtered


def _print_summary(
    scores: list[EvalScore], agent_name: str, pass_threshold: float = 0.8
):
    table = Table(title=f"Results: {agent_name}")
    table.add_column("Task", style="cyan")
    table.add_column("Score", justify="right")
    table.add_column("pass@k", justify="right")
    table.add_column("Status", justify="center")

    for s in scores:
        status = "PASS" if s.score >= pass_threshold else "FAIL"
        pk = f"{s.pass_at_k:.0%}" if s.pass_at_k is not None else "-"
        table.add_row(s.task_id, f"{s.score:.2f}", pk, status)

    avg = sum(s.score for s in scores) / max(len(scores), 1)
    table.add_section()
    table.add_row("[bold]Average[/bold]", f"[bold]{avg:.2f}[/bold]", "", "")

    console.print(table)


def _save_results(
    scores: list[EvalScore],
    agent_name: str,
    output_dir: Path,
    pass_threshold: float = 0.8,
):
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
            "pass_rate": sum(1 for s in scores if s.score >= pass_threshold)
            / max(len(scores), 1),
        },
    }

    path.write_text(json.dumps(data, indent=2))
    logger.info("Results saved to %s", path)
    console.print(f"\n[dim]Results saved to {path}[/dim]")
