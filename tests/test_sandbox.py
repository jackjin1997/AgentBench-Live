"""Tests for sandbox environment management."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentbench.sandbox import Sandbox
from agentbench.schema import (
    AutoEvalConfig,
    Difficulty,
    Domain,
    EvalConfig,
    EvalType,
    SetupConfig,
    Task,
)


def _make_task(network: bool = False, install: str = "", files: list | None = None) -> Task:
    return Task(
        id="sandbox-test",
        version=1,
        domain=Domain.CODE,
        difficulty=Difficulty.EASY,
        title="Sandbox Test",
        description="Test task for sandbox",
        human_time_minutes=5,
        setup=SetupConfig(
            files=files or [],
            install=install,
            network=network,
        ),
        prompt="Do the thing in /workspace",
        evaluation=EvalConfig(type=EvalType.AUTO, timeout_seconds=60),
    )


class TestSandboxLifecycle:
    def test_setup_creates_workspace(self):
        task = _make_task()
        sandbox = Sandbox(task)
        try:
            workspace = sandbox.setup()
            assert workspace.exists()
            assert workspace.is_dir()
            assert "agentbench-sandbox-test" in str(workspace)
        finally:
            sandbox.cleanup()

    def test_cleanup_removes_workspace(self):
        task = _make_task()
        sandbox = Sandbox(task)
        workspace = sandbox.setup()
        assert workspace.exists()
        sandbox.cleanup()
        assert not workspace.exists()

    def test_context_manager(self):
        task = _make_task()
        with Sandbox(task) as sandbox:
            assert sandbox.workspace.exists()
            ws_path = sandbox.workspace
        assert not ws_path.exists()

    def test_workspace_before_setup_raises(self):
        task = _make_task()
        sandbox = Sandbox(task)
        with pytest.raises(RuntimeError, match="not set up"):
            _ = sandbox.workspace

    def test_double_cleanup_safe(self):
        task = _make_task()
        sandbox = Sandbox(task)
        sandbox.setup()
        sandbox.cleanup()
        sandbox.cleanup()  # Should not raise


class TestSandboxPrompt:
    def test_resolve_prompt(self):
        task = _make_task()
        with Sandbox(task) as sandbox:
            resolved = sandbox.resolve_prompt("Edit /workspace/app.py")
            assert str(sandbox.workspace) in resolved
            assert "/workspace" not in resolved

    def test_resolve_prompt_no_workspace_ref(self):
        task = _make_task()
        with Sandbox(task) as sandbox:
            resolved = sandbox.resolve_prompt("Just do something")
            assert resolved == "Just do something"


class TestSandboxEnv:
    def test_network_enabled_full_env(self):
        task = _make_task(network=True)
        with Sandbox(task) as sandbox:
            env = sandbox._build_env()
            assert "WORKSPACE" in env
            assert "PATH" in env
            assert env["WORKSPACE"] == str(sandbox.workspace)

    def test_network_disabled_minimal_env(self):
        task = _make_task(network=False)
        with Sandbox(task) as sandbox:
            env = sandbox._build_env()
            assert set(env.keys()) == {"PATH", "HOME", "WORKSPACE"}

    def test_network_enabled_property(self):
        task = _make_task(network=True)
        sandbox = Sandbox(task)
        assert sandbox.network_enabled is True

    def test_network_disabled_property(self):
        task = _make_task(network=False)
        sandbox = Sandbox(task)
        assert sandbox.network_enabled is False


class TestSandboxCommand:
    def test_run_command_success(self):
        task = _make_task()
        with Sandbox(task) as sandbox:
            result = sandbox.run_command("echo hello")
            assert result.returncode == 0
            assert "hello" in result.stdout

    def test_run_command_resolves_workspace(self):
        task = _make_task()
        with Sandbox(task) as sandbox:
            # Create a file in workspace
            (sandbox.workspace / "test.txt").write_text("content")
            result = sandbox.run_command("cat /workspace/test.txt")
            assert "content" in result.stdout

    def test_run_command_failure(self):
        task = _make_task()
        with Sandbox(task) as sandbox:
            result = sandbox.run_command("false")
            assert result.returncode != 0


class TestSandboxInstall:
    @patch("agentbench.sandbox.platform")
    def test_adapt_install_filters_apt_on_darwin(self, mock_platform):
        mock_platform.system.return_value = "Darwin"
        task = _make_task(install="apt-get install -y git && pip install requests")
        sandbox = Sandbox(task)
        sandbox._workspace = Path("/tmp/fake")
        result = sandbox._adapt_install_for_local(task.setup.install)
        assert "apt-get" not in result
        assert "pip install requests" in result

    @patch("agentbench.sandbox.platform")
    def test_adapt_install_keeps_all_on_linux(self, mock_platform):
        mock_platform.system.return_value = "Linux"
        task = _make_task(install="apt-get install -y git && pip install requests")
        sandbox = Sandbox(task)
        sandbox._workspace = Path("/tmp/fake")
        result = sandbox._adapt_install_for_local(task.setup.install)
        assert "apt-get" in result
        assert "pip install requests" in result

    def test_adapt_install_empty(self):
        task = _make_task()
        sandbox = Sandbox(task)
        assert sandbox._adapt_install_for_local("") == ""
        assert sandbox._adapt_install_for_local("   ") == ""

    @patch("agentbench.sandbox.platform")
    def test_adapt_install_all_apt_filtered(self, mock_platform):
        mock_platform.system.return_value = "Darwin"
        task = _make_task(install="apt-get update && apt-get install -y git")
        sandbox = Sandbox(task)
        sandbox._workspace = Path("/tmp/fake")
        result = sandbox._adapt_install_for_local(task.setup.install)
        assert result == ""

    def test_install_timeout_configurable(self):
        task = _make_task()
        sandbox = Sandbox(task, install_timeout=60)
        assert sandbox._install_timeout == 60
