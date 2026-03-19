"""Sandbox for isolated task execution."""

from __future__ import annotations

import logging
import os
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path

from agentbench.schema import Task

logger = logging.getLogger(__name__)

# Environment variables to pass through to agent subprocesses when
# network access is enabled (local tempdir mode).
_NETWORK_ENV_PASSTHROUGH = [
    "PATH", "HOME", "USER", "SHELL", "LANG", "TERM",
    "GH_TOKEN", "GITHUB_TOKEN", "GH_ENTERPRISE_TOKEN",
    "ANTHROPIC_API_KEY", "OPENAI_API_KEY",
    "PYTHONPATH", "NODE_PATH", "NVM_DIR", "VIRTUAL_ENV", "CONDA_PREFIX",
    "HOMEBREW_PREFIX", "HOMEBREW_CELLAR", "HOMEBREW_REPOSITORY",
    "XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME",
    "SSH_AUTH_SOCK",
    "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY",
    "http_proxy", "https_proxy", "no_proxy",
]


class Sandbox:
    """Manages an isolated workspace for task execution.

    For MVP, uses local temporary directories with subprocess isolation.
    """

    def __init__(self, task: Task, install_timeout: int = 120):
        self.task = task
        self._workspace: Path | None = None
        self._install_timeout = install_timeout

    def setup(self) -> Path:
        """Create and populate the sandbox workspace."""
        self._workspace = Path(tempfile.mkdtemp(prefix=f"agentbench-{self.task.id}-"))
        logger.info("Created sandbox workspace: %s", self._workspace)

        # Copy fixture files into workspace
        for file_mapping in self.task.setup.files:
            src = Path("tasks") / file_mapping["src"]
            raw_dst = file_mapping.get("dst", "").strip("/")
            if raw_dst == "workspace" or raw_dst == "":
                dst = self._workspace
            else:
                dst = self._workspace / raw_dst
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            elif src.is_file():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

        # Run install commands
        if self.task.setup.install:
            install_cmd = self._adapt_install_for_local(self.task.setup.install)
            if install_cmd:
                logger.info("Running install command: %s", install_cmd)
                env = self._build_env()
                subprocess.run(
                    install_cmd,
                    shell=True,
                    cwd=str(self._workspace),
                    capture_output=True,
                    timeout=self._install_timeout,
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
        return self.task.setup.network

    def resolve_prompt(self, prompt: str) -> str:
        """Replace /workspace references in a prompt with the actual workspace path."""
        return prompt.replace("/workspace", str(self.workspace))

    def _build_env(self) -> dict[str, str]:
        """Build environment dict for subprocess execution."""
        if self.network_enabled:
            env = {**os.environ, "WORKSPACE": str(self.workspace)}
        else:
            env = {
                "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
                "HOME": os.environ.get("HOME", "/tmp"),
                "WORKSPACE": str(self.workspace),
            }
        return env

    def run_command(self, command: str, timeout: int = 60) -> subprocess.CompletedProcess:
        """Run a command inside the sandbox workspace."""
        resolved_cmd = command.replace("/workspace", str(self.workspace))
        env = self._build_env()
        logger.debug("Running command in sandbox: %s", resolved_cmd)
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
        """Adapt Docker-oriented install commands for local execution."""
        if not install_cmd or not install_cmd.strip():
            return ""

        install_cmd = install_cmd.replace("/workspace", str(self.workspace))

        if platform.system() == "Darwin":
            parts = [p.strip() for p in install_cmd.split("&&")]
            filtered = [p for p in parts if not p.startswith(("apt-get", "apt ", "dpkg"))]
            return " && ".join(filtered) if filtered else ""

        return install_cmd

    def cleanup(self):
        """Remove the sandbox workspace."""
        if self._workspace and self._workspace.exists():
            shutil.rmtree(self._workspace, ignore_errors=True)
            logger.info("Cleaned up sandbox workspace: %s", self._workspace)
            self._workspace = None

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, *args):
        self.cleanup()
