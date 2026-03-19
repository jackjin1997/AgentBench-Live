# AgentBench-Live

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/Tests-160_passed-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/Coverage-90%25-brightgreen.svg)](tests/)
[![Agents Tested](https://img.shields.io/badge/Agents_Tested-2-green.svg)](#-leaderboard)

**The open benchmark for AI agent task execution.**

> We don't test how well agents *chat*. We test how well they *get things done*.

AgentBench-Live evaluates AI coding agents on **real-world tasks** — writing code, analyzing data, orchestrating multi-step workflows, using tools, and conducting research — inside sandboxed environments, then scores them automatically.

No vibes. No self-reported evals. Just results.

---

## 🏆 Leaderboard

**[Live Leaderboard](https://jackjin1997.github.io/AgentBench-Live/)** | Full 10-task benchmark results (updated 2026-03-15):

| Rank | Agent | Avg Score | Pass Rate | Best Domain |
|:---:|:---|:---:|:---:|:---|
| 1 | **Claude Code** | **0.74** | 5/10 | Code (1.00) |
| 2 | **Gemini CLI** | **0.52** | 3/10 | Code (1.00) |

<details>
<summary><b>Full task-by-task breakdown</b></summary>

| Task | Domain | Claude Code | Gemini CLI | Delta |
|:---|:---|:---:|:---:|:---:|
| code-001 | Code | 1.00 ✅ | 1.00 ✅ | 0.00 |
| code-002 | Code | 1.00 ✅ | 1.00 ✅ | 0.00 |
| data-001 | Data | 0.88 ✅ | 0.28 ❌ | **+0.60** |
| data-002 | Data | 0.70 ❌ | 0.70 ❌ | 0.00 |
| multi-001 | Multi-step | 0.88 ✅ | 0.60 ❌ | +0.28 |
| multi-002 | Multi-step | 0.88 ✅ | 0.88 ✅ | 0.00 |
| research-001 | Research | 0.70 ❌ | 0.00 ❌ | +0.70 |
| research-002 | Research | 0.70 ❌ | 0.70 ❌ | 0.00 |
| tool-001 | Tool Use | 0.70 ❌ | 0.00 ❌ | **+0.70** |
| tool-002† | Tool Use | 0.00 ❌ | 0.00 ❌ | 0.00 |

> † `tool-002` scored 0.00 for both agents due to a sandbox validation issue. Scores without LLM-as-Judge use fallback scoring (output presence check); set `ANTHROPIC_API_KEY` for full evaluation.

</details>

---

## 📊 Domain Breakdown

| Domain | Tasks | Claude Code | Gemini CLI | Winner |
|:---|:---:|:---:|:---:|:---|
| **Code** | 2 | 1.00 | 1.00 | Tie |
| **Data Analysis** | 2 | 0.79 | 0.49 | Claude Code |
| **Multi-step** | 2 | 0.88 | 0.74 | Claude Code |
| **Research** | 2 | 0.70 | 0.35 | Claude Code |
| **Tool Use** | 2 | 0.35 | 0.00 | Claude Code |

---

## 💡 Notable Findings

- **Both agents ace pure code tasks.** Code generation and bug fixing are effectively solved — perfect scores from both agents across both code challenges.
- **Claude Code dominates data analysis.** The biggest gap between agents: Claude Code scored 0.88 vs Gemini CLI's 0.28 on `data-001`, a +0.60 delta.
- **Multi-step workflows separate the best from the rest.** Tasks requiring planning across multiple tools and steps reveal meaningful differences: Claude Code averaged 0.88, Gemini CLI 0.74.
- **Claude Code handles real-world tools; Gemini CLI doesn't.** On tasks requiring GitHub CLI and web research, Claude Code scored 0.70 while Gemini CLI scored 0.00 — suggesting Gemini CLI struggles with tool-heavy tasks outside its sandbox.

---

## 🚀 Quick Start

```bash
# Install
pip install agentbench-live

# Run the full benchmark against an agent
agentbench run --agent claude-code --tasks all

# Run a single domain
agentbench run --agent gemini-cli --domain data

# Compare two agents head-to-head
agentbench compare claude-code gemini-cli

# View the leaderboard
agentbench leaderboard
```

---

## 🏗️ Architecture

```
agentbench-live/
├── tasks/           # Benchmark task definitions (YAML)
├── adapters/        # Agent-specific adapters
├── sandbox/         # Docker sandbox runner
├── evaluators/      # Scoring engines (auto + LLM-as-Judge)
├── ranking/         # ELO calculation & history
├── leaderboard/     # Static frontend (GitHub Pages)
└── docs/            # Documentation & methodology
```

**How a benchmark run works:**

1. **Task** — A structured challenge with inputs, environment setup, and expected outcomes
2. **Sandbox** — A fresh Docker container with pre-configured tooling
3. **Agent** — Receives the task prompt and works autonomously inside the sandbox
4. **Evaluator** — Scores the output using automated tests, LLM-as-Judge, or both
5. **Ranking** — ELO update based on pairwise comparisons across agents

---

## 🔧 Capability Domains

| Domain | What We Test | How We Score |
|:---|:---|:---|
| **Code** | Bug fixes, feature implementation, refactoring | Test pass rate + diff quality |
| **Research** | Technical investigation, comparison reports | LLM-as-Judge + human review |
| **Data** | CSV/JSON analysis, insight generation | Accuracy + insight quality |
| **Tool Use** | API calls, MCP tools, file operations | Success rate + efficiency |
| **Multi-step** | Complex workflows across multiple tools | End-to-end success + time |

---

## 🤖 Add Your Agent

AgentBench-Live supports any CLI-based or IDE-based agent through adapters. To add yours:

1. **Create an adapter** in `adapters/your_agent.py`:

```python
from agentbench.adapter import BaseAdapter

class YourAgentAdapter(BaseAdapter):
    name = "your-agent"

    def execute(self, task_prompt: str, sandbox: Sandbox) -> str:
        """Send the task to your agent and return its output."""
        # Launch your agent CLI inside the sandbox
        # Capture and return the result
        ...
```

2. **Register it** in `adapters/__init__.py`

3. **Test it** against the benchmark:

```bash
agentbench run --agent your-agent --tasks code-001
```

4. **Submit a PR** — once it passes, your agent joins the leaderboard.

See the [adapter authoring guide](docs/adapter-authoring.md) for the full specification.

---

## 🤝 Contributing

We welcome contributions in three forms:

- **New Tasks** — Submit benchmark tasks via PR ([task authoring guide](docs/task-authoring.md))
- **New Adapters** — Add support for your favorite agent ([adapter guide](docs/adapter-authoring.md))
- **Evaluator Improvements** — Better scoring heuristics and judges

---

## 📄 License

MIT

---

Built with the belief that the best way to improve agents is to measure them honestly.
