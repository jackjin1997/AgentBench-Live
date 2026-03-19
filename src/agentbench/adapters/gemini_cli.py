"""Adapter for Google Gemini CLI agent."""

from agentbench.adapters.base import AgentAdapter
from agentbench.adapters.registry import register_adapter


@register_adapter
class GeminiCLIAdapter(AgentAdapter):
    """Adapter for Google's Gemini CLI."""

    name = "gemini-cli"
    cli_command = "gemini"
    api_key_env_var = "GEMINI_API_KEY"

    def _build_command(self, prompt: str) -> list[str]:
        return ["gemini", "--non-interactive", "-p", prompt]
