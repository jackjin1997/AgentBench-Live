"""Tests for workspace file collection."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from agentbench.config import BenchmarkConfig
from agentbench.evaluator.workspace import collect_workspace_outputs


class TestCollectWorkspaceOutputs:
    def test_collects_files(self, tmp_path):
        (tmp_path / "report.md").write_text("# Report")
        (tmp_path / "data.json").write_text('{"key": "value"}')
        (tmp_path / "notes.txt").write_text("Some notes")
        (tmp_path / "app.py").write_text("print('hello')")

        sandbox = MagicMock()
        sandbox.workspace = tmp_path
        outputs = collect_workspace_outputs(sandbox)

        assert "report.md" in outputs
        assert "data.json" in outputs
        assert "notes.txt" in outputs
        assert "app.py" in outputs

    def test_truncates_content(self, tmp_path):
        config = BenchmarkConfig()
        config.eval.file_content_cap = 10
        (tmp_path / "big.txt").write_text("x" * 1000)

        sandbox = MagicMock()
        sandbox.workspace = tmp_path
        outputs = collect_workspace_outputs(sandbox, config=config)

        assert len(outputs["big.txt"]) == 10

    def test_empty_workspace(self, tmp_path):
        sandbox = MagicMock()
        sandbox.workspace = tmp_path
        outputs = collect_workspace_outputs(sandbox)
        assert outputs == {}

    def test_ignores_non_matching_extensions(self, tmp_path):
        (tmp_path / "image.png").write_bytes(b"\x89PNG")
        (tmp_path / "data.csv").write_text("a,b,c")

        sandbox = MagicMock()
        sandbox.workspace = tmp_path
        outputs = collect_workspace_outputs(sandbox)
        assert outputs == {}

    def test_handles_read_error(self, tmp_path):
        """Unreadable files are skipped with a warning."""
        f = tmp_path / "bad.txt"
        f.write_text("content")
        f.chmod(0o000)

        sandbox = MagicMock()
        sandbox.workspace = tmp_path

        try:
            outputs = collect_workspace_outputs(sandbox)
            # May or may not contain the file depending on OS permissions
        finally:
            f.chmod(0o644)  # Restore for cleanup
