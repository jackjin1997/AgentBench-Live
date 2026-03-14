# 🏆 AgentBench-Live

**The real-time leaderboard for AI agent task execution.**

> We don't test how well agents *chat*. We test how well they *get things done*.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is AgentBench-Live?

AgentBench-Live is an open-source benchmark that evaluates AI agents on **real-world task execution** — writing code, conducting research, analyzing data, using tools, and orchestrating multi-step workflows.

Unlike chat-focused benchmarks, we measure what matters: **can your agent actually do the job?**

## Key Features

- **5 Capability Domains**: Code, Research, Data Analysis, Tool Use, Multi-step Workflows
- **Real-time ELO Rankings**: Live leaderboard updated with every benchmark run
- **Sandboxed Execution**: Every task runs in an isolated Docker container
- **CLI-Agent First**: Native support for Claude Code, OpenClaw, Gemini CLI, and more
- **Community Tasks**: Submit your own benchmark tasks via PR
- **Open Evaluation**: Automated scoring + LLM-as-Judge + human review

## Quick Start

```bash
# Install
pip install agentbench-live

# Run a benchmark against Claude Code
agentbench run --agent claude-code --tasks all

# Run a specific domain
agentbench run --agent claude-code --domain code --difficulty easy

# View leaderboard
agentbench leaderboard
```

## Capability Domains

| Domain | What We Test | Scoring |
|:---|:---|:---|
| 🔧 **Code** | Bug fixes, feature implementation, refactoring | Test pass rate + diff quality |
| 🔍 **Research** | Technical investigation, comparison reports | LLM-as-Judge + human review |
| 📊 **Data** | CSV/JSON analysis, insight generation | Accuracy + insight quality |
| 🛠️ **Tool Use** | API calls, MCP tools, file operations | Success rate + efficiency |
| 🧩 **Multi-step** | Complex workflows across multiple tools | End-to-end success + time |

## Supported Agents

| Agent | Status | Type |
|:---|:---:|:---|
| Claude Code | ✅ | CLI |
| OpenClaw | ✅ | CLI |
| Gemini CLI | ✅ | CLI |
| Codex CLI | 🔜 | CLI |
| Cline | 🔜 | IDE |
| Cursor Agent | 🔜 | IDE |

## Architecture

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

## How It Works

1. **Task** → A structured challenge with inputs, environment, and expected outcomes
2. **Sandbox** → Fresh Docker container with pre-configured tooling
3. **Agent** → Receives the task prompt, works autonomously in the sandbox
4. **Evaluator** → Scores the output (automated tests, LLM judge, or human review)
5. **Ranking** → ELO update based on pairwise comparisons across agents

## Contributing

We welcome contributions in three forms:

- **New Tasks**: Submit benchmark tasks via PR ([task authoring guide](docs/task-authoring.md))
- **New Adapters**: Add support for your favorite agent
- **Evaluator Improvements**: Better scoring heuristics and judges

## License

MIT

---

Built with the belief that the best way to improve agents is to measure them honestly.
