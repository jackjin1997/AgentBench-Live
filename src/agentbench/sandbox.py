"""Docker sandbox for isolated task execution."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from agentbench.schema import Task


@dataclass
class SandboxConfig:
    """Configuration for a sandbox environment."""

    workspace: Path
    base_image: str
    network: bool
    timeout_seconds: int


# Environment variables to pass through to agent subprocesses when
# network access is enabled (local tempdir mode).
_NETWORK_ENV_PASSTHROUGH = [
    "PATH", "HOME", "USER", "SHELL", "LANG", "TERM",
    # GitHub CLI / API auth
    "GH_TOKEN", "GITHUB_TOKEN", "GH_ENTERPRISE_TOKEN",
    # Common API keys agents may need
    "ANTHROPIC_API_KEY", "OPENAI_API_KEY",
    # Python / Node environment
    "PYTHONPATH", "NODE_PATH", "NVM_DIR", "VIRTUAL_ENV", "CONDA_PREFIX",
    # macOS-specific
    "HOMEBREW_PREFIX", "HOMEBREW_CELLAR", "HOMEBREW_REPOSITORY",
    # XDG dirs (used by gh, etc.)
    "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME",
    # SSH (for git operations)
    "SSH_AUTH_SOCK",
    # Proxy settings
    "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY",
    "http_proxy", "https_proxy", "no_proxy",
]


class Sandbox:
    """Manages an isolated workspace for task execution.

    For MVP, uses local temporary directories with subprocess isolation.
    Docker-based isolation is the next step (Task #5 full implementation).
    """

    def __init__(self, task: Task):
        self.task = task
        self._workspace: Path | None = None

    def setup(self) -> Path:
        """Create and populate the sandbox workspace."""
        self._workspace = Path(tempfile.mkdtemp(prefix=f"agentbench-{self.task.id}-"))

        # Copy fixture files into workspace
        for file_mapping in self.task.setup.files:
            src = Path("tasks") / file_mapping["src"]
            raw_dst = file_mapping.get("dst", "").strip("/")
            # In local mode, /workspace/ maps to the tmpdir root
            if raw_dst == "workspace" or raw_dst == "":
                dst = self._workspace
            else:
                dst = self._workspace / raw_dst
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            elif src.is_file():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

        # Run install commands (skip Docker-only commands in local mode)
        if self.task.setup.install:
            install_cmd = self._adapt_install_for_local(self.task.setup.install)
            if install_cmd:
                env = self._build_env()
                subprocess.run(
                    install_cmd,
                    shell=True,
                    cwd=str(self._workspace),
                    capture_output=True,
                    timeout=120,
                    env=env,
                )

        return self._workspace

    @property
    def workspace(self) -> Path:
        if self._workspace is None:
            raise RuntimeError("Sandbox not set up. Call setup() first.")
        return self._workspace

    @property
    def network_enabled(self) -> bool:
        """Whether this sandbox's task requires network access."""
        return self.task.setup.network

    def resolve_prompt(self, prompt: str) -> str:
        """Replace /workspace references in a prompt with the actual workspace path."""
        return prompt.replace("/workspace", str(self.workspace))

    def _build_env(self) -> dict[str, str]:
        """Build environment dict for subprocess execution.

        In local tempdir mode, passes through the user's environment
        when network is enabled (needed for gh auth, API tokens, etc.).
        When network is disabled, uses a minimal environment.
        """
        if self.network_enabled:
            # Pass through the full user environment plus WORKSPACE
            env = {**os.environ, "WORKSPACE": str(self.workspace)}
        else:
            # Minimal environment for sandboxed execution
            env = {
                "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                "HOME": os.environ.get("HOME", "/tmp"),
                "WORKSPACE": str(self.workspace),
            }
        return env

    def run_command(self, command: str, timeout: int = 60) -> subprocess.CompletedProcess:
        """Run a command inside the sandbox workspace."""
        # Replace /workspace references with actual tmpdir path
        resolved_cmd = command.replace("/workspace", str(self.workspace))
        env = self._build_env()
        return subprocess.run(
            resolved_cmd,
            shell=True,
            cwd=str(self.workspace),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )

    def _adapt_install_for_local(self, install_cmd: str) -> str:
        """Adapt Docker-oriented install commands for local execution.

        In local tempdir mode (not Docker), commands like 'apt-get install'
        don't work on macOS and may require sudo on Linux. Skip them and
        rely on the tools being pre-installed on the host.
        """
        if not install_cmd or not install_cmd.strip():
            return ""

        # Replace /workspace with actual path
        install_cmd = install_cmd.replace("/workspace", str(self.workspace))

        # On macOS, skip apt-get commands entirely (tools should be pre-installed)
        if platform.system() == "Darwin":
            # Filter out apt-get commands from compound commands
            parts = [p.strip() for p in install_cmd.split("&&")]
            filtered = [p for p in parts if not p.startswith(("apt-get", "apt ", "dpkg"))]
            return " && ".join(filtered) if filtered else ""

        return install_cmd

    def cleanup(self):
        """Remove the sandbox workspace."""
        if self._workspace and self._workspace.exists():
            shutil.rmtree(self._workspace, ignore_errors=True)
            self._workspace = None

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, *args):
        self.cleanup()
