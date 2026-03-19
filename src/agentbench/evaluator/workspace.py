"""Workspace file collection for evaluation."""

from __future__ import annotations

import logging

from agentbench.config import BenchmarkConfig, load_config
from agentbench.sandbox import Sandbox

logger = logging.getLogger(__name__)

OUTPUT_EXTENSIONS = ("*.md", "*.json", "*.txt", "*.py")


def collect_workspace_outputs(
    sandbox: Sandbox,
    config: BenchmarkConfig | None = None,
) -> dict[str, str]:
    """Read key output files from the workspace.

    Returns:
        Mapping of filename to (truncated) content.
    """
    cfg = config or load_config()
    cap = cfg.eval.file_content_cap
    outputs: dict[str, str] = {}

    for ext in OUTPUT_EXTENSIONS:
        for f in sandbox.workspace.glob(ext):
            try:
                outputs[f.name] = f.read_text()[:cap]
            except OSError as exc:
                logger.warning("Failed to read workspace file %s: %s", f, exc)

    return outputs
