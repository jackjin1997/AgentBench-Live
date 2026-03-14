"""Adapter registry for managing available agent adapters."""

from agentbench.adapters.base import AgentAdapter

_REGISTRY: dict[str, type[AgentAdapter]] = {}


def register_adapter(cls: type[AgentAdapter]) -> type[AgentAdapter]:
    """Register an adapter class. Use as a decorator."""
    _REGISTRY[cls.name] = cls
    return cls


def get_adapter(name: str) -> AgentAdapter:
    """Get an adapter instance by name."""
    if name not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY.keys()))
        raise ValueError(f"Unknown agent: {name!r}. Available: {available}")
    return _REGISTRY[name]()


def list_adapters() -> list[str]:
    """List all registered adapter names."""
    return sorted(_REGISTRY.keys())
