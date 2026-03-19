"""Adapter for Google Gemini CLI agent."""

from agentbench.adapters.base import AgentAdapter
from agentbench.adapters.registry import register_adapter


@register_adapter
class GeminiCLIAdapter(AgentAdapter):
    """Adapter for Google's Gemini CLI.

    Uses stdin mode so Gemini can execute sandbox commands
    and modify files in the workspace.
    """

    name = "gemini-cli"
    cli_command = "gemini"
    api_key_env_var = "GEMINI_API_KEY"
    prompt_via_stdin = True

    def _build_command(self, prompt: str) -> list[str]:
        return ["gemini"]
