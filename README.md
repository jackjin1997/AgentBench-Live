<div align="center">

# AgentBench-Live

### The benchmark that tests what agents *do*, not what they *say*.

Real tasks. Real sandboxes. Real scores. No vibes.

[![CI](https://github.com/jackjin1997/AgentBench-Live/actions/workflows/ci.yml/badge.svg)](https://github.com/jackjin1997/AgentBench-Live/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/Tests-183_passed-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/Coverage-90%25-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Release](https://img.shields.io/badge/Release-v0.1.0-blue.svg)](https://github.com/jackjin1997/AgentBench-Live/releases/tag/v0.1.0)

[Live Leaderboard](https://jackjin1997.github.io/AgentBench-Live/) | [Methodology](docs/methodology.md) | [Contributing](CONTRIBUTING.md)

</div>

---

Most agent benchmarks test toy problems or let agents self-report. AgentBench-Live drops agents into **Docker-sandboxed workspaces** with real codebases, real data files, and real multi-step workflows — then scores them automatically with test suites and LLM judges.

**Why not SWE-bench / OpenHarness?** Those benchmark a single axis (GitHub issue resolution). We test **5 capability domains** — code, data analysis, multi-step orchestration, research, and tool use — because real work isn't just fixing bugs.

---

## Leaderboard

> **10 tasks across 5 domains** | Docker sandbox | Auto-eval + LLM Judge scoring

| Agent | Code | Data | Multi-Step | Research | Tool Use | **Overall** |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Claude Code** | 1.00 | 0.07 | 0.74 | 0.60 | 0.25 | **0.53** |
| **Gemini CLI** | 1.00 | 0.32 | 0.77 | 0.45 | 0.05 | **0.52** |
| Codex CLI | - | - | - | - | - | *pending* |
| Aider | - | - | - | - | - | *pending* |

<details>
<summary><b>Full task-level breakdown</b></summary>

| Task | Domain | Claude Code | Gemini CLI |
|:---|:---|:---:|:---:|
| code-001 | Code | 1.00 | 1.00 |
| code-002 | Code | 1.00 | 1.00 |
| data-001 | Data | 0.04 | 0.04 |
| data-002 | Data | 0.10 | 0.60 |
| multi-001 | Multi-Step | 0.64 | 0.70 |
| multi-002 | Multi-Step | 0.84 | 0.84 |
| research-001 | Research | 0.60 | 0.30 |
| research-002 | Research | 0.60 | 0.60 |
| tool-001 | Tool Use | 0.50 | 0.10 |
| tool-002 | Tool Use | 0.00 | 0.00 |

</details>

---

## Add Your Agent in 15 Lines

This is the entire Claude Code adapter. Yours looks the same:

```python
from agentbench.adapters.base import AgentAdapter
from agentbench.adapters.registry import register_adapter

@register_adapter
class YourAgentAdapter(AgentAdapter):
    name = "your-agent"
    cli_command = "your-cli"
    api_key_env_var = "YOUR_API_KEY"

    def _build_command(self, prompt: str) -> list[str]:
        return ["your-cli", "--run", prompt]
```

Submit a PR with your adapter. Your agent joins the leaderboard.

---

## Quick Start

```bash
# Clone and install
git clone https://github.com/jackjin1997/AgentBench-Live.git
cd AgentBench-Live
pip install -e ".[dev]"

# Run the full benchmark
agentbench run --agent claude-code --tasks all

# Run a single domain
agentbench run --agent gemini-cli --domain code

# View results
agentbench leaderboard

# Generate a shareable comparison card
agentbench social-card --output comparison.png
```

---

## How It Works

```
Task (YAML) → Docker Sandbox → Agent Execution → Auto-Eval + LLM Judge → Score
```

1. **Task** — A structured YAML challenge with inputs, environment setup, and expected outcomes
2. **Sandbox** — Docker prepares an isolated workspace. Falls back to local tempdir if Docker is unavailable
3. **Agent** — Receives the prompt and works autonomously inside the sandbox
4. **Evaluator** — Scores output using pytest (code tasks), heuristics, or LLM-as-Judge
5. **Ranking** — Scores aggregated per domain and overall, published to the leaderboard

### Capability Domains

| Domain | What We Test | How We Score |
|:---|:---|:---|
| **Code** | Bug fixes, feature implementation, refactoring | pytest pass rate |
| **Data** | CSV/JSON analysis, insight generation | Accuracy + insight quality |
| **Multi-step** | Complex workflows across multiple tools | End-to-end success |
| **Research** | Technical investigation, comparison reports | LLM-as-Judge |
| **Tool Use** | API calls, CLI tools, file operations | Success rate |

See the [full methodology](docs/methodology.md) for details on task design, scoring, and reproducibility.

---

## Currently Benchmarked

| Agent | Adapter | Status |
|:---|:---|:---:|
| [Claude Code](https://github.com/anthropics/claude-code) | `claude-code` | Benchmarked |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) | `gemini-cli` | Benchmarked |
| [Codex CLI](https://github.com/openai/codex) | `codex-cli` | Ready (run pending) |
| [Aider](https://github.com/Aider-AI/aider) | `aider` | Ready (run pending) |

## Wanted: Community Adapters

We'd love help adding adapters for these agents. Each one is ~15 lines of Python:

- **[Cursor](https://github.com/getcursor/cursor)** — [open issue](https://github.com/jackjin1997/AgentBench-Live/issues)
- **[Windsurf](https://github.com/codeium/windsurf)** — [open issue](https://github.com/jackjin1997/AgentBench-Live/issues)
- **[OpenHands](https://github.com/All-Hands-AI/OpenHands)** — [open issue](https://github.com/jackjin1997/AgentBench-Live/issues)
- **[Devin](https://github.com/cognition-ai/devin)** — [open issue](https://github.com/jackjin1997/AgentBench-Live/issues)
- **Your agent** — [see contributing guide](CONTRIBUTING.md)

---

## Architecture

```
agentbench-live/
├── src/agentbench/
│   ├── adapters/       # Agent adapters (template method pattern)
│   ├── evaluator/      # Auto-eval, LLM judge, composite scoring
│   ├── sandbox.py      # Docker + local sandbox (SandboxFactory)
│   ├── runner.py       # Benchmark orchestrator
│   └── cli.py          # CLI entry point (click)
├── tasks/              # 10 benchmark tasks across 5 domains (YAML)
├── leaderboard/        # Static frontend (GitHub Pages)
├── docs/               # Methodology & guides
└── tests/              # 183 tests, 90% coverage
```

---

## Contributing

- **Add an agent** — Write an adapter (~15 lines), submit a PR
- **Add tasks** — Submit new benchmark tasks ([task authoring guide](docs/task-authoring.md))
- **Improve scoring** — Better heuristics, judges, evaluation methods
- **Run benchmarks** — Run existing agents and submit results

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

---

## License

MIT

---

<div align="center">

*Built with the belief that the best way to improve agents is to measure them honestly.*

</div>
