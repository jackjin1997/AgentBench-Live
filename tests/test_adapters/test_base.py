"""Tests for base adapter template method."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentbench.adapters.base import AgentAdapter, AgentResult


class ConcreteAdapter(AgentAdapter):
    """Test adapter for testing base class behavior."""

    name = "test-adapter"
    cli_command = "echo"
    api_key_env_var = "TEST_API_KEY"

    def _build_command(self, prompt: str) -> list[str]:
        return ["echo", prompt]


class NoKeyAdapter(AgentAdapter):
    """Adapter with no API key."""

    name = "no-key"
    cli_command = "echo"

    def _build_command(self, prompt: str) -> list[str]:
        return ["echo", prompt]


class TestAgentAdapterRun:
    def test_successful_run(self, tmp_path):
        adapter = ConcreteAdapter()
        result = adapter.run(
            prompt="hello world",
            workspace=tmp_path,
            timeout_seconds=10,
        )
        assert result.success is True
        assert result.exit_code == 0
        assert "hello world" in result.stdout
        assert result.agent_name == "test-adapter"
        assert result.duration_seconds > 0

    def test_timeout_handling(self, tmp_path):
        adapter = ConcreteAdapter()
        with patch("agentbench.adapters.base.subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(cmd="echo", timeout=1)
            result = adapter.run(
                prompt="test",
                workspace=tmp_path,
                timeout_seconds=1,
            )
        assert result.success is False
        assert result.exit_code == -1
        assert "Timeout" in result.stderr

    def test_task_id_empty_by_default(self, tmp_path):
        adapter = ConcreteAdapter()
        result = adapter.run(prompt="test", workspace=tmp_path)
        assert result.task_id == ""


class TestAgentAdapterEnv:
    def test_network_true_full_env(self, tmp_path, monkeypatch):
        monkeypatch.setenv("SOME_VAR", "some_value")
        adapter = ConcreteAdapter()
        env = adapter._build_env(tmp_path, network=True)
        assert "SOME_VAR" in env
        assert env["WORKSPACE"] == str(tmp_path)

    def test_network_false_minimal_env(self, tmp_path, monkeypatch):
        monkeypatch.setenv("TEST_API_KEY", "secret123")
        adapter = ConcreteAdapter()
        env = adapter._build_env(tmp_path, network=False)
        assert set(env.keys()) == {"PATH", "HOME", "WORKSPACE", "TEST_API_KEY"}
        assert env["TEST_API_KEY"] == "secret123"

    def test_no_api_key_env(self, tmp_path):
        adapter = NoKeyAdapter()
        env = adapter._build_env(tmp_path, network=False)
        assert set(env.keys()) == {"PATH", "HOME", "WORKSPACE"}

    def test_missing_api_key_empty_string(self, tmp_path, monkeypatch):
        monkeypatch.delenv("TEST_API_KEY", raising=False)
        adapter = ConcreteAdapter()
        env = adapter._build_env(tmp_path, network=False)
        assert env["TEST_API_KEY"] == ""


class TestAgentAdapterAvailability:
    def test_available(self):
        adapter = ConcreteAdapter()  # echo always exists
        assert adapter.is_available() is True

    def test_not_available(self):
        adapter = ConcreteAdapter()
        adapter.cli_command = "nonexistent_command_xyz"
        assert adapter.is_available() is False

    def test_no_cli_command(self):
        adapter = ConcreteAdapter()
        adapter.cli_command = ""
        assert adapter.is_available() is False

    def test_timeout_in_availability_check(self):
        adapter = ConcreteAdapter()
        with patch("agentbench.adapters.base.subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(cmd="echo", timeout=10)
            assert adapter.is_available() is False


class TestAgentAdapterRepr:
    def test_repr(self):
        adapter = ConcreteAdapter()
        assert "ConcreteAdapter" in repr(adapter)
        assert "test-adapter" in repr(adapter)
