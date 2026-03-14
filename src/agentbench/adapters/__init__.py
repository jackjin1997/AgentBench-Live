"""Agent adapters for running benchmark tasks against different CLI agents."""

from agentbench.adapters.base import AgentAdapter, AgentResult
from agentbench.adapters.registry import get_adapter, list_adapters, register_adapter

__all__ = [
    "AgentAdapter",
    "AgentResult",
    "get_adapter",
    "list_adapters",
    "register_adapter",
]
