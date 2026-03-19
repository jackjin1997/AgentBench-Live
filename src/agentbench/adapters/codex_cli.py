"""Adapter for OpenAI Codex CLI agent."""

from agentbench.adapters.base import AgentAdapter
from agentbench.adapters.registry import register_adapter


@register_adapter
class CodexCLIAdapter(AgentAdapter):
    """Adapter for OpenAI's Codex CLI."""

    name = "codex-cli"
    cli_command = "codex"
    api_key_env_var = "OPENAI_API_KEY"

    def _build_command(self, prompt: str) -> list[str]:
        return ["codex", "--quiet", "--auto-edit", prompt]
