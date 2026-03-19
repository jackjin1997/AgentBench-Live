"""Tests for CLI commands."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from agentbench.cli import main


@pytest.fixture
def runner():
    return CliRunner()


class TestCLI:
    def test_help(self, runner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "AgentBench-Live" in result.output

    def test_version(self, runner):
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0


class TestTasksCommand:
    def test_tasks_list(self, runner, tmp_path):
        yaml_content = """
id: cli-test-001
domain: code
difficulty: easy
title: CLI Test Task
description: A task for testing CLI
prompt: "Do it"
"""
        (tmp_path / "test.yaml").write_text(yaml_content)
        result = runner.invoke(main, ["tasks", "--tasks-dir", str(tmp_path)])
        assert result.exit_code == 0
        assert "cli-test-001" in result.output

    def test_tasks_filter_domain(self, runner, tmp_path):
        for domain in ["code", "research"]:
            yaml_content = f"""
id: {domain}-001
domain: {domain}
difficulty: easy
title: {domain} task
description: A {domain} task
prompt: "Do {domain}"
"""
            (tmp_path / f"{domain}.yaml").write_text(yaml_content)

        result = runner.invoke(main, ["tasks", "--tasks-dir", str(tmp_path), "--domain", "code"])
        assert result.exit_code == 0
        assert "code-001" in result.output
        assert "research-001" not in result.output

    def test_tasks_empty_dir(self, runner, tmp_path):
        result = runner.invoke(main, ["tasks", "--tasks-dir", str(tmp_path)])
        assert result.exit_code == 0


class TestAgentsCommand:
    def test_agents_list(self, runner):
        result = runner.invoke(main, ["agents"])
        assert result.exit_code == 0
        assert "claude-code" in result.output


class TestRunCommand:
    @patch("agentbench.runner.run_benchmark")
    def test_run_basic(self, mock_run, runner):
        mock_run.return_value = []
        result = runner.invoke(main, [
            "run", "--agent", "claude-code",
            "--trials", "1", "--domain", "code",
        ])
        assert mock_run.called or result.exit_code == 0


class TestLeaderboardCommand:
    def test_leaderboard_no_results(self, runner, tmp_path):
        result = runner.invoke(main, ["leaderboard", "--results-dir", str(tmp_path)])
        assert result.exit_code == 0
        assert "No results found" in result.output

    def test_leaderboard_with_results(self, runner, sample_results_dir):
        result = runner.invoke(main, [
            "leaderboard", "--results-dir", str(sample_results_dir)
        ])
        assert result.exit_code == 0
        assert "test-agent" in result.output
