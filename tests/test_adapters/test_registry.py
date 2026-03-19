"""Tests for adapter registry."""

from __future__ import annotations

import pytest

from agentbench.adapters.base import AgentAdapter
from agentbench.adapters.registry import (
    _REGISTRY,
    get_adapter,
    list_adapters,
    register_adapter,
)


class TestRegistry:
    def test_register_adapter(self):
        original_registry = dict(_REGISTRY)

        class DummyAdapter(AgentAdapter):
            name = "dummy-test"
            cli_command = "dummy"

            def _build_command(self, prompt):
                return ["dummy", prompt]

        register_adapter(DummyAdapter)
        assert "dummy-test" in _REGISTRY

        # Cleanup
        del _REGISTRY["dummy-test"]

    def test_get_adapter_known(self):
        # claude-code should be registered via module import
        import agentbench.adapters.claude_code  # noqa: F401

        adapter = get_adapter("claude-code")
        assert adapter.name == "claude-code"

    def test_get_adapter_unknown(self):
        with pytest.raises(ValueError, match="Unknown agent"):
            get_adapter("nonexistent-agent-xyz")

    def test_list_adapters(self):
        import agentbench.adapters.claude_code  # noqa: F401

        names = list_adapters()
        assert isinstance(names, list)
        assert "claude-code" in names
        assert names == sorted(names)
