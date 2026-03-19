"""Tests for sandbox environment management."""

from __future__ import annotations

import os
import shutil
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


class TestDockerAvailable:
    """Tests for the _docker_available() static method."""

    @patch("agentbench.sandbox.subprocess.run")
    def test_docker_available_returns_true(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        assert Sandbox._docker_available() is True
        mock_run.assert_called_once_with(
            ["docker", "info"],
            capture_output=True,
            timeout=10,
        )

    @patch("agentbench.sandbox.subprocess.run")
    def test_docker_available_returns_false_on_nonzero(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1)
        assert Sandbox._docker_available() is False

    @patch("agentbench.sandbox.subprocess.run", side_effect=FileNotFoundError)
    def test_docker_available_returns_false_when_not_installed(self, mock_run):
        assert Sandbox._docker_available() is False

    @patch(
        "agentbench.sandbox.subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="docker info", timeout=10),
    )
    def test_docker_available_returns_false_on_timeout(self, mock_run):
        assert Sandbox._docker_available() is False

    @patch("agentbench.sandbox.subprocess.run", side_effect=OSError("connection refused"))
    def test_docker_available_returns_false_on_os_error(self, mock_run):
        assert Sandbox._docker_available() is False


class TestDockerModeSetup:
    """Tests for Docker mount-mode setup flow."""

    @patch("agentbench.sandbox.subprocess.run")
    @patch.object(Sandbox, "_docker_available", return_value=True)
    def test_docker_setup_no_install(self, mock_avail, mock_run):
        """Docker mode: create container, copy files out, remove container."""
        mock_run.return_value = MagicMock(returncode=0)
        task = _make_task()
        sandbox = Sandbox(task)
        try:
            workspace = sandbox.setup()
            assert workspace.exists()
            # Should have called: docker create, docker cp (workspace out), docker rm
            calls = [c[0][0] for c in mock_run.call_args_list]
            assert any(c[0] == "docker" and "create" in c for c in calls)
            assert any(c[0] == "docker" and "rm" in c for c in calls)
        finally:
            sandbox.cleanup()

    @patch("agentbench.sandbox.subprocess.run")
    @patch.object(Sandbox, "_docker_available", return_value=True)
    def test_docker_setup_with_install(self, mock_avail, mock_run):
        """Docker mode with install: create, start, exec, copy, rm."""
        mock_run.return_value = MagicMock(returncode=0)
        task = _make_task(install="pip install requests")
        sandbox = Sandbox(task)
        try:
            workspace = sandbox.setup()
            assert workspace.exists()
            calls = [c[0][0] for c in mock_run.call_args_list]
            # Verify docker exec was called for install
            assert any(c[0] == "docker" and "exec" in c for c in calls)
            # Verify docker start was called before exec
            assert any(c[0] == "docker" and "start" in c for c in calls)
        finally:
            sandbox.cleanup()

    @patch("agentbench.sandbox.subprocess.run")
    @patch.object(Sandbox, "_docker_available", return_value=True)
    def test_docker_setup_with_files(self, mock_avail, mock_run):
        """Docker mode copies fixture files into the container."""
        import tempfile as tf

        # Create a real fixture file so src.exists() is True
        tmp = Path(tf.mkdtemp())
        tasks_dir = tmp / "tasks" / "fixture"
        tasks_dir.mkdir(parents=True)
        (tasks_dir / "hello.txt").write_text("hello")

        mock_run.return_value = MagicMock(returncode=0)
        task = _make_task(files=[{"src": "fixture/hello.txt", "dst": "workspace"}])
        sandbox = Sandbox(task)

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp)
            workspace = sandbox.setup()
            assert workspace.exists()
            # Should have a docker cp call for the fixture file
            calls = [c[0][0] for c in mock_run.call_args_list]
            cp_calls = [c for c in calls if c[0] == "docker" and "cp" in c]
            # At least 2 cp calls: one for file in, one for workspace out
            assert len(cp_calls) >= 2
        finally:
            os.chdir(original_cwd)
            sandbox.cleanup()
            shutil.rmtree(tmp, ignore_errors=True)


class TestDockerFallback:
    """Tests for fallback to local mode."""

    @patch.object(Sandbox, "_docker_available", return_value=False)
    def test_fallback_when_docker_unavailable(self, mock_avail):
        """Falls back to local tempdir when Docker is not available."""
        task = _make_task()
        sandbox = Sandbox(task)
        try:
            workspace = sandbox.setup()
            assert workspace.exists()
            assert workspace.is_dir()
            assert "agentbench-sandbox-test" in str(workspace)
        finally:
            sandbox.cleanup()

    @patch("agentbench.sandbox.subprocess.run")
    @patch.object(Sandbox, "_docker_available", return_value=True)
    def test_fallback_when_docker_create_fails(self, mock_avail, mock_run):
        """Falls back to local mode when docker create fails."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "docker create"
        )
        task = _make_task()
        sandbox = Sandbox(task)
        try:
            workspace = sandbox.setup()
            # Should still get a valid workspace via local fallback
            assert workspace.exists()
            assert workspace.is_dir()
        finally:
            sandbox.cleanup()

    @patch("agentbench.sandbox.subprocess.run")
    @patch.object(Sandbox, "_docker_available", return_value=True)
    def test_fallback_when_docker_exec_fails(self, mock_avail, mock_run):
        """Falls back to local mode when docker exec (install) fails."""
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            cmd = args[0] if args else kwargs.get("command", [])
            # Let docker create succeed, fail on exec
            if isinstance(cmd, list) and len(cmd) > 1:
                if cmd[1] == "exec":
                    raise subprocess.CalledProcessError(1, "docker exec")
            return MagicMock(returncode=0)

        mock_run.side_effect = side_effect
        task = _make_task(install="pip install something")
        sandbox = Sandbox(task)
        try:
            workspace = sandbox.setup()
            assert workspace.exists()
        finally:
            sandbox.cleanup()
