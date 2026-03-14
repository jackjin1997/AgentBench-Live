"""Adapter for OpenAI Codex CLI agent."""

import subprocess
import time
from pathlib import Path

from agentbench.adapters.base import AgentAdapter, AgentResult
from agentbench.adapters.registry import register_adapter


@register_adapter
class CodexCLIAdapter(AgentAdapter):
    """Adapter for OpenAI's Codex CLI."""

    name = "codex-cli"

    def run(
        self,
        prompt: str,
        workspace: Path,
        timeout_seconds: int = 300,
        network: bool = False,
    ) -> AgentResult:
        start = time.monotonic()
        try:
            result = subprocess.run(
                [
                    "codex",
                    "--quiet",
                    "--auto-edit",
                    prompt,
                ],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                cwd=str(workspace),
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
            return AgentResult(
                agent_name=self.name,
                task_id="",
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Timeout after {timeout_seconds}s",
                duration_seconds=duration,
            )

    def is_available(self) -> bool:
        try:
            result = subprocess.run(
                ["codex", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
