"""Base adapter interface for CLI agents."""

from __future__ import annotations

import logging
import os
import subprocess
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """Result from an agent executing a task."""

    agent_name: str
    task_id: str
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    output_files: dict[str, str] = field(default_factory=dict)
    tool_call_count: int = 0
    transcript: str = ""


class AgentAdapter(ABC):
    """Base class for CLI agent adapters.

    Subclasses only need to define class attributes and implement
    ``_build_command()`` — the base class handles subprocess execution,
    environment building, timeout handling, and availability checks.
    """

    name: str = "base"
    cli_command: str = ""
    api_key_env_var: str = ""
    prompt_via_stdin: bool = False  # If True, prompt is piped via stdin

    def run(
        self,
        prompt: str,
        workspace: Path,
        timeout_seconds: int = 300,
        network: bool = False,
    ) -> AgentResult:
        """Run the agent on a task prompt inside the given workspace."""
        start = time.monotonic()
        cmd = self._build_command(prompt)
        env = self._build_env(workspace, network)

        stdin_input = prompt if self.prompt_via_stdin else None

        try:
            result = subprocess.run(
                cmd,
                input=stdin_input,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                cwd=str(workspace),
                env=env,
            )
            duration = time.monotonic() - start
            return AgentResult(
                agent_name=self.name,
                task_id="",
                success=result.returncode == 0,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                duration_seconds=duration,
            )
        except subprocess.TimeoutExpired:
            duration = time.monotonic() - start
            logger.warning(
                "Agent %s timed out after %ds", self.name, timeout_seconds
            )
            return AgentResult(
                agent_name=self.name,
                task_id="",
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Timeout after {timeout_seconds}s",
                duration_seconds=duration,
            )

    @abstractmethod
    def _build_command(self, prompt: str) -> list[str]:
        """Build the CLI command to invoke the agent.

        Args:
            prompt: The task prompt to send to the agent.

        Returns:
            Command as a list of strings (for subprocess).
        """
        ...

    def _build_env(self, workspace: Path, network: bool) -> dict[str, str]:
        """Build environment for the agent subprocess."""
        if network:
            return {**os.environ, "WORKSPACE": str(workspace)}

        env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": os.environ.get("HOME", "/tmp"),
            "WORKSPACE": str(workspace),
        }
        if self.api_key_env_var:
            env[self.api_key_env_var] = os.environ.get(self.api_key_env_var, "")
        return env

    def is_available(self) -> bool:
        """Check if this agent's CLI is installed and accessible."""
        if not self.cli_command:
            return False
        try:
            result = subprocess.run(
                [self.cli_command, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"
