"""Adapter for Claude Code CLI agent."""

from agentbench.adapters.base import AgentAdapter
from agentbench.adapters.registry import register_adapter


@register_adapter
class ClaudeCodeAdapter(AgentAdapter):
    """Adapter for Anthropic's Claude Code CLI."""

    name = "claude-code"
    cli_command = "claude"
    api_key_env_var = "ANTHROPIC_API_KEY"

    def _build_command(self, prompt: str) -> list[str]:
        return ["claude", "--print", "--dangerously-skip-permissions", prompt]
