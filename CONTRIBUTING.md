# Contributing to AgentBench-Live

Thanks for your interest in improving how we measure AI agents.

## Ways to Contribute

### Add a New Agent Adapter (~15 lines)

The fastest way to contribute. Create `src/agentbench/adapters/your_agent.py`:

```python
from agentbench.adapters.base import AgentAdapter
from agentbench.adapters.registry import register_adapter


@register_adapter
class YourAgentAdapter(AgentAdapter):
    """Adapter for Your Agent CLI."""

    name = "your-agent"
    cli_command = "your-cli"
    api_key_env_var = "YOUR_API_KEY"  # optional; remove if no key needed
    prompt_via_stdin = True            # set False to pass via argv instead

    def _build_command(self, prompt: str) -> list[str]:
        return ["your-cli", "--run"]
```

The base class handles sandbox setup, environment isolation, timeout enforcement, and output capture. You only define the CLI invocation.

Add the import to `src/agentbench/adapters/__init__.py` so the registry picks it up, run the benchmark on at least one task, and submit a PR with your results.

Reference adapters live in `src/agentbench/adapters/{claude_code,gemini_cli,codex_cli,aider}.py` — read those before writing your own.

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
