"""Base adapter interface for CLI agents."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


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
    # Files created/modified by the agent in the workspace
    output_files: dict[str, str] = field(default_factory=dict)
    # Number of tool calls / commands the agent executed
    tool_call_count: int = 0
    # Raw transcript of agent's actions (if available)
    transcript: str = ""


class AgentAdapter(ABC):
    """Base class for CLI agent adapters.

    Each adapter knows how to invoke a specific CLI agent, pass it
    a task prompt, and capture its output from within a sandbox.
    """

    name: str = "base"

    @abstractmethod
    def run(
        self,
        prompt: str,
        workspace: Path,
        timeout_seconds: int = 300,
        network: bool = False,
    ) -> AgentResult:
        """Run the agent on a task prompt inside the given workspace.

        Args:
            prompt: The task prompt to send to the agent.
            workspace: Path to the sandbox workspace directory.
            timeout_seconds: Max execution time before killing the agent.
            network: Whether the agent should have network access.

        Returns:
            AgentResult with captured output and metadata.
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this agent is installed and accessible."""
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"
