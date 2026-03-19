"""Adapter for Aider CLI agent."""

from agentbench.adapters.base import AgentAdapter
from agentbench.adapters.registry import register_adapter


@register_adapter
class AiderAdapter(AgentAdapter):
    """Adapter for Aider (AI pair programming in the terminal)."""

    name = "aider"
    cli_command = "aider"
    api_key_env_var = "OPENAI_API_KEY"

    def _build_command(self, prompt: str) -> list[str]:
        return ["aider", "--yes-always", "--no-git", "--message", prompt]
