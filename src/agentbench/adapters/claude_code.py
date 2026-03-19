"""Adapter for Claude Code CLI agent."""

from agentbench.adapters.base import AgentAdapter
from agentbench.adapters.registry import register_adapter


@register_adapter
class ClaudeCodeAdapter(AgentAdapter):
    """Adapter for Anthropic's Claude Code CLI.

    Uses interactive mode (not --print) so Claude Code can actually
    read/write files and run commands in the workspace.
    Prompt is piped via stdin.
    """

    name = "claude-code"
    cli_command = "claude"
    api_key_env_var = "ANTHROPIC_API_KEY"
    prompt_via_stdin = True

    def _build_command(self, prompt: str) -> list[str]:
        return ["claude", "--dangerously-skip-permissions"]
