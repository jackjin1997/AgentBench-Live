# AgentBench-Live

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/Tests-183_passed-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/Coverage-90%25-brightgreen.svg)](tests/)
[![Agents Tested](https://img.shields.io/badge/Agents_Tested-4-green.svg)](#-leaderboard)

**The open benchmark for AI agent task execution.**

> We don't test how well agents *chat*. We test how well they *get things done*.

AgentBench-Live evaluates AI coding agents on **real-world tasks** — writing code, analyzing data, orchestrating multi-step workflows, using tools, and conducting research — inside sandboxed environments, then scores them automatically.

No vibes. No self-reported evals. Just results.

---

## Leaderboard

**[Live Leaderboard](https://jackjin1997.github.io/AgentBench-Live/)** | Full 10-task benchmark results:

> Scores will be updated after the next full benchmark run with Docker sandbox + LLM Judge scoring across all 4 agents.

### Supported Agents

| Agent | CLI | Status |
|:---|:---|:---:|
| **Claude Code** | `claude` | Benchmarked |
| **Gemini CLI** | `gemini` | Benchmarked |
| **Codex CLI** | `codex` | Ready |
| **Aider** | `aider` | Ready |

---

## How It Works

```
Task (YAML) → Docker Sandbox → Agent Execution → Auto-Eval + LLM Judge → Score
```

1. **Task** — A structured challenge with inputs, environment setup, and expected outcomes
2. **Sandbox** — Docker prepares a clean workspace with dependencies installed. Falls back to local tempdir if Docker is unavailable.
3. **Agent** — Receives the task prompt and works autonomously in the workspace
4. **Evaluator** — Scores the output using automated tests, LLM-as-Judge, or both
5. **Ranking** — Scores aggregated per domain and overall

See the [full methodology](docs/methodology.md) for details on task design, scoring, and reproducibility.

---

## Quick Start

```bash
# Install
pip install agentbench-live

# Run the full benchmark against an agent
agentbench run --agent claude-code --tasks all

# Run a single domain
agentbench run --agent aider --domain code

# View the leaderboard
agentbench leaderboard

# Generate a social comparison card
agentbench social-card --output comparison.png
```

---

## Capability Domains

| Domain | What We Test | How We Score |
|:---|:---|:---|
| **Code** | Bug fixes, feature implementation, refactoring | Test pass rate |
| **Data** | CSV/JSON analysis, insight generation | Accuracy + insight quality |
| **Multi-step** | Complex workflows across multiple tools | End-to-end success |
| **Research** | Technical investigation, comparison reports | LLM-as-Judge |
| **Tool Use** | API calls, CLI tools, file operations | Success rate |

---

## Add Your Agent

Any CLI-based agent can be added in ~50 lines of Python:

```python
from agentbench.adapters.base import AgentAdapter
from agentbench.adapters.registry import register_adapter

@register_adapter
class YourAgentAdapter(AgentAdapter):
    name = "your-agent"
    cli_command = "your-agent-cli"
    api_key_env_var = "YOUR_API_KEY"

    def _build_command(self, prompt: str) -> list[str]:
        return ["your-agent-cli", "--prompt", prompt]
```

Then run:
```bash
agentbench run --agent your-agent --tasks code-001
```

Submit a PR with your adapter + results, and your agent joins the leaderboard.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

---

## Architecture

```
agentbench-live/
├── src/agentbench/     # Core framework
│   ├── adapters/       # Agent adapters (claude-code, gemini-cli, codex-cli, aider)
│   ├── evaluator/      # Scoring (auto-eval, LLM judge, composite)
│   ├── sandbox.py      # Docker + local sandbox
│   ├── runner.py       # Benchmark orchestrator
│   └── cli.py          # CLI entry point
├── tasks/              # Benchmark task definitions (YAML)
├── leaderboard/        # Static frontend (GitHub Pages)
├── docs/               # Methodology & guides
└── tests/              # 183 tests, 90% coverage
```

---

## Contributing

- **New Tasks** — Submit benchmark tasks via PR ([task authoring guide](docs/task-authoring.md))
- **New Adapters** — Add support for your favorite agent
- **Evaluator Improvements** — Better scoring heuristics and judges

---

## License

MIT

---

Built with the belief that the best way to improve agents is to measure them honestly.
