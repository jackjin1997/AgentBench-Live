"""Docker sandbox for isolated task execution."""

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
            dst = self._workspace / file_mapping.get("dst", "").lstrip("/")
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            elif src.is_file():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

        # Run install commands
        if self.task.setup.install:
            subprocess.run(
                self.task.setup.install,
                shell=True,
                cwd=str(self._workspace),
                capture_output=True,
                timeout=120,
            )

        return self._workspace

    @property
    def workspace(self) -> Path:
        if self._workspace is None:
            raise RuntimeError("Sandbox not set up. Call setup() first.")
        return self._workspace

    def run_command(self, command: str, timeout: int = 60) -> subprocess.CompletedProcess:
        """Run a command inside the sandbox workspace."""
        return subprocess.run(
            command,
            shell=True,
            cwd=str(self.workspace),
            capture_output=True,
            text=True,
            timeout=timeout,
        )

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
