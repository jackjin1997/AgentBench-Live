# Contributing to AgentBench-Live

Thanks for your interest in improving how we measure AI agents.

## Ways to Contribute

### Add a New Agent Adapter (~50 lines)

The fastest way to contribute. Create `src/agentbench/adapters/your_agent.py`:

```python
from agentbench.adapters.base import BaseAdapter, AgentResult

class YourAgentAdapter(BaseAdapter):
    name = "your-agent"
    command = "your-agent-cli"

    def run(self, prompt, workspace, timeout_seconds, network):
        result = subprocess.run(
            [self.command, "--prompt", prompt],
            cwd=str(workspace),
            capture_output=True, text=True,
            timeout=timeout_seconds,
        )
        return AgentResult(
            agent_name=self.name,
            stdout=result.stdout,
            returncode=result.returncode,
        )
```

Register it in `src/agentbench/adapters/__init__.py`, run the benchmark, and submit a PR with your results.

### Add a New Benchmark Task

See the [task authoring guide](docs/task-authoring.md). Good tasks are:

- **Deterministic** — same input always allows the same correct output
- **Self-contained** — fixtures include everything needed
- **Time-calibrated** — annotated with human completion time
- **Auto-scorable** — has automated tests or clear LLM-judge rubric

### Improve Scoring

The evaluator (`src/agentbench/evaluator.py`) supports auto tests, LLM-as-Judge, and composite scoring. Ideas:

- Better pytest output parsing
- More robust LLM judge prompts
- Domain-specific scoring heuristics

## Development Setup

```bash
git clone https://github.com/jackjin1997/AgentBench-Live.git
cd AgentBench-Live
pip install -e ".[dev]"

# Run the benchmark
agentbench run --agent claude-code --domain code --trials 1

# Run tests
pytest
```

## PR Guidelines

- One feature/fix per PR
- Include benchmark results if adding an agent or task
- Keep changes focused — don't refactor unrelated code

## Questions?

Open an issue or start a discussion. We're happy to help.
