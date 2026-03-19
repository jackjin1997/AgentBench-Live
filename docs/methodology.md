# Methodology

## Overview

AgentBench-Live evaluates AI coding agents on **real-world task execution** — not chat quality, not vibes, not self-reported metrics. Each agent receives the same task prompt, works in an isolated workspace, and is scored by automated tests and/or LLM-as-Judge.

## Task Design

### Selection Criteria

Tasks are designed to test capabilities that matter in real development workflows:

| Domain | What We Test | Example |
|:---|:---|:---|
| **Code** | Bug fixes, feature implementation | Fix off-by-one error in pagination |
| **Data** | CSV/JSON analysis, insights | Analyze sales data and generate summary |
| **Multi-step** | Complex workflows across tools | Refactor + test + document a module |
| **Research** | Technical investigation | Compare database options for a use case |
| **Tool Use** | API calls, file operations | Set up GitHub Actions workflow |

Each task must be:
- **Deterministic** — the same correct output is always achievable
- **Self-contained** — all fixtures and test cases are included
- **Time-calibrated** — annotated with estimated human completion time
- **Auto-scorable** — has automated tests, LLM-judge rubric, or both

### Task Format

Tasks are defined as YAML files with structured fields:

```yaml
id: code-001
domain: code
difficulty: easy
title: "Fix off-by-one error in pagination"
prompt: "Fix the bug in paginator.py so all tests pass"
setup:
  files:
    - src: fixtures/code-001
      dst: workspace
  install: "pip install pytest"
evaluation:
  type: auto
  auto:
    command: "cd /workspace && python -m pytest test_paginator.py -v"
```

## Scoring

### Evaluation Types

1. **Auto (`auto`)** — runs a test command (usually pytest) and scores based on pass rate. Score = tests_passed / tests_total. Fully deterministic.

2. **LLM Judge (`llm-judge`)** — sends the agent's output and a rubric to an LLM evaluator (Claude Sonnet by default). The judge scores each rubric criterion on a 1-10 scale. Final score = average / 10.

3. **Composite (`composite`)** — weighted combination of auto (60%) and LLM judge (40%). Used for tasks where both test results and output quality matter.

### Pass Threshold

An agent "passes" a task if its score ≥ 0.80. This threshold was chosen to require strong (not just partial) solutions.

### Fallback Scoring

When no LLM API key is configured, tasks using LLM-judge evaluation fall back to heuristic scoring (capped at 0.60). This is clearly marked in results. For authoritative scores, set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`.

### pass@k

When running multiple trials (e.g., `--trials 3`), pass@k = (trials where score ≥ 0.80) / total_trials. The leaderboard reports the best score across trials.

## Execution Environment

### Sandbox

Each task runs in an isolated workspace:

- **Docker mode (recommended):** A fresh Docker container prepares the workspace — installs dependencies, copies fixture files. The agent then works against this clean environment. This ensures reproducibility across machines.
- **Local mode (fallback):** When Docker is unavailable, a local temporary directory is used. Results may vary based on the host environment.

### Agent Execution

Agents receive:
1. A text prompt describing the task
2. A workspace directory with pre-configured files
3. A timeout (default 300 seconds)

The agent runs as a subprocess and can execute any commands within the workspace. Network access is enabled only for tasks that require it (research, tool-use domains).

### What Agents Cannot Do

- Access other tasks' workspaces
- Read the evaluation criteria or test cases
- Modify the benchmark framework itself

## Reproducibility

To reproduce our results:

```bash
git clone https://github.com/jackjin1997/AgentBench-Live
cd AgentBench-Live
pip install -e ".[eval]"
export ANTHROPIC_API_KEY=your-key  # for LLM judge scoring

# Run full benchmark
agentbench run --agent claude-code --tasks all
agentbench run --agent gemini-cli --tasks all
```

Results depend on:
- Agent version (we report the version used)
- Docker availability (for reproducible sandboxing)
- LLM judge availability (for non-auto tasks)
- Network access (for research/tool-use tasks)

## Limitations

- **Small task set.** 10 tasks across 5 domains is a starting point, not exhaustive. We actively seek task contributions.
- **Agent availability.** Not all agents have CLI interfaces suitable for automated benchmarking. IDE-based agents (Cursor, Windsurf) cannot currently be tested.
- **LLM judge variance.** LLM-as-judge scores have inherent variance (~±0.05). Auto-eval tasks are fully deterministic.
- **Single-turn only.** Tasks test one-shot execution. Multi-turn interaction patterns are not yet evaluated.

## Contributing Tasks

See the [task authoring guide](task-authoring.md) for the full specification. Good benchmark tasks test real capabilities, not trick questions.
