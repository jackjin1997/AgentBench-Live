<div align="center">

# AgentBench-Live

### We re-ran the same coding agent twice. The score went from 0.0 to 0.7.

Most agent leaderboards report a single number. We don't think that's honest.

[![CI](https://github.com/jackjin1997/AgentBench-Live/actions/workflows/ci.yml/badge.svg)](https://github.com/jackjin1997/AgentBench-Live/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/Tests-183_passed-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/Coverage-90%25-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Release](https://img.shields.io/badge/Release-v0.2.0-blue.svg)](https://github.com/jackjin1997/AgentBench-Live/releases)

[Live Leaderboard](https://jackjin1997.github.io/AgentBench-Live/) · [Methodology](docs/methodology.md) · [Findings](docs/findings.md) · [Contributing](CONTRIBUTING.md)

</div>

---

## What we found

Three things that surprised us when we benchmarked Claude Code and Gemini CLI on 10 real-world tasks:

**1 · "Tied overall" hides 7× per-axis gaps.**
Overall scores look close (Claude 0.63, Gemini 0.52). But on **Tool Use**, Claude is **7× better**. On **Multi-Step**, Gemini is slightly ahead. **The average lies. Pick the agent for the task, not the leaderboard.**

**2 · Code tasks are commodity now.**
Both agents score **1.00 on every code task** (`code-001`, `code-002`). "Which AI writes code better" is the wrong question in 2026. The interesting differences live in tool calling, research, and multi-step orchestration.

**3 · Re-running the same agent on the same task gives wildly different scores.**
Claude Code on `tool-001`: **0.0 in trial 1, 0.7 in trial 2**. Same agent, same task, same prompt. Most agent leaderboards quietly publish a single trial. We think that's misleading.

→ **Full data, methodology, and per-task breakdown: [docs/findings.md](docs/findings.md)**

---

## Leaderboard

> **10 tasks across 5 domains** · Docker sandbox · Auto-eval (pytest) + LLM-as-Judge

### Per-domain (where the real differences live)

| Domain | Claude Code | Gemini CLI | Gap | Verdict |
|:---|:---:|:---:|:---:|:---|
| Code | **1.00** | **1.00** | 1.0× | Tied — code is solved |
| Data | 0.49 | 0.32 | 1.5× | Claude leads |
| Multi-Step | 0.74 | 0.77 | 1.0× | Gemini slight edge |
| Research | 0.70 | 0.45 | **1.6×** | Claude clearly leads |
| **Tool Use** | **0.35** | **0.05** | **7.0×** | **Claude dominates** |
| Overall | 0.63 | 0.52 | 1.2× | — |

### Variance (the part nobody publishes)

| Agent | Run 1 | Run 2 | Run 3 | Spread |
|:---|:---:|:---:|:---:|:---:|
| Claude Code | 0.604 | 0.656 | — | **±5%** |
| Gemini CLI | 0.516 | 0.516 | 0.518 | ±0.4% |

Single-trial benchmarks ignore this. We won't.

| Agent | Adapter | Status |
|:---|:---|:---:|
| [Claude Code](https://github.com/anthropics/claude-code) | `claude-code` | ✅ Benchmarked |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) | `gemini-cli` | ✅ Benchmarked |
| [Codex CLI](https://github.com/openai/codex) | `codex-cli` | 🔄 Adapter ready, multi-trial run pending |
| [Aider](https://github.com/Aider-AI/aider) | `aider` | 🔄 Adapter ready, multi-trial run pending |

---

## What makes us different

Most agent benchmarks (SWE-bench, PinchBench, ClawProBench, OSWorld) optimize for **headline numbers**. We optimize for **honest numbers**.

| | Most leaderboards | AgentBench-Live |
|:---|:---|:---|
| Trials per task | 1 | ≥3 (target: 5) |
| Reports variance | ❌ | ✅ min / max / median |
| Reports cost | ❌ | 🔄 v0.3 |
| Reports latency | ❌ | 🔄 v0.3 |
| Sandbox | tempdir / mocks | Docker (real isolation) |
| Adapter overhead | ~hundreds of LOC | **~15 lines of Python** |
| Open source | varies | MIT, every line |

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

# Run the full benchmark with multiple trials
agentbench run --agent claude-code --tasks all --trials 3

# Compare two agents on a single domain
agentbench run --agents claude-code,gemini-cli --domain tool-use --trials 5

# View results with variance
agentbench leaderboard --show-variance

# Generate a shareable comparison card
agentbench social-card --output comparison.png
```

---

## How It Works

```
Task (YAML) → Docker Sandbox → Agent Execution × N trials → Auto-Eval + LLM Judge → Score (mean ± stdev)
```

1. **Task** — A structured YAML challenge with inputs, environment setup, and expected outcomes
2. **Sandbox** — Docker prepares an isolated workspace. Falls back to local tempdir if Docker is unavailable
3. **Agent** — Receives the prompt and works autonomously inside the sandbox; **runs N independent trials**
4. **Evaluator** — Scores output using pytest (code tasks), heuristics, or LLM-as-Judge
5. **Aggregator** — Reports mean, median, min, max, and pass@k across trials
6. **Leaderboard** — Per-domain scores with variance bars, published to GitHub Pages

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

## Wanted: Community Adapters

We'd love help adding adapters for these agents. Each one is ~15 lines of Python:

- **[Cursor](https://cursor.com)** — IDE-native agent
- **[Windsurf](https://windsurf.com)** — Codeium's agent
- **[OpenHands](https://github.com/All-Hands-AI/OpenHands)** — open-source autonomous dev
- **[Devin](https://devin.ai)** — Cognition's autonomous engineer
- **Your agent** — [see contributing guide](CONTRIBUTING.md)

[Open an issue](https://github.com/jackjin1997/AgentBench-Live/issues/new) to claim one.

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
├── docs/               # Methodology, findings, guides
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

MIT — every line, no asterisks.

---

<div align="center">

*The best way to improve agents is to measure them honestly — variance and all.*

</div>
