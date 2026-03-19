"""Adapter for OpenClaw CLI agent."""

from agentbench.adapters.base import AgentAdapter
from agentbench.adapters.registry import register_adapter


@register_adapter
class OpenClawAdapter(AgentAdapter):
    """Adapter for OpenClaw CLI."""

    name = "openclaw"
    cli_command = "claw"

    def _build_command(self, prompt: str) -> list[str]:
        return ["claw", "run", "--non-interactive", "--prompt", prompt]
