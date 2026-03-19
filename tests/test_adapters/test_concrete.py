"""Tests for concrete adapter implementations."""

from __future__ import annotations

from agentbench.adapters.aider import AiderAdapter
from agentbench.adapters.claude_code import ClaudeCodeAdapter
from agentbench.adapters.codex_cli import CodexCLIAdapter
from agentbench.adapters.gemini_cli import GeminiCLIAdapter
from agentbench.adapters.openclaw import OpenClawAdapter


class TestClaudeCodeAdapter:
    def test_name(self):
        assert ClaudeCodeAdapter.name == "claude-code"

    def test_cli_command(self):
        assert ClaudeCodeAdapter.cli_command == "claude"

    def test_api_key(self):
        assert ClaudeCodeAdapter.api_key_env_var == "ANTHROPIC_API_KEY"

    def test_build_command(self):
        adapter = ClaudeCodeAdapter()
        cmd = adapter._build_command("Fix the bug")
        assert cmd == ["claude", "--dangerously-skip-permissions"]

    def test_prompt_via_stdin(self):
        assert ClaudeCodeAdapter.prompt_via_stdin is True


class TestOpenClawAdapter:
    def test_name(self):
        assert OpenClawAdapter.name == "openclaw"

    def test_cli_command(self):
        assert OpenClawAdapter.cli_command == "claw"

    def test_no_api_key(self):
        assert OpenClawAdapter.api_key_env_var == ""

    def test_build_command(self):
        adapter = OpenClawAdapter()
        cmd = adapter._build_command("Analyze data")
        assert cmd == ["claw", "run", "--non-interactive", "--prompt", "Analyze data"]


class TestGeminiCLIAdapter:
    def test_name(self):
        assert GeminiCLIAdapter.name == "gemini-cli"

    def test_cli_command(self):
        assert GeminiCLIAdapter.cli_command == "gemini"

    def test_api_key(self):
        assert GeminiCLIAdapter.api_key_env_var == "GEMINI_API_KEY"

    def test_build_command(self):
        adapter = GeminiCLIAdapter()
        cmd = adapter._build_command("Write code")
        assert cmd == ["gemini"]

    def test_prompt_via_stdin(self):
        assert GeminiCLIAdapter.prompt_via_stdin is True


class TestAiderAdapter:
    def test_name(self):
        assert AiderAdapter.name == "aider"

    def test_cli_command(self):
        assert AiderAdapter.cli_command == "aider"

    def test_api_key(self):
        assert AiderAdapter.api_key_env_var == "OPENAI_API_KEY"

    def test_build_command(self):
        adapter = AiderAdapter()
        cmd = adapter._build_command("Refactor the code")
        assert cmd == ["aider", "--yes-always", "--no-git", "--message", "Refactor the code"]


class TestCodexCLIAdapter:
    def test_name(self):
        assert CodexCLIAdapter.name == "codex-cli"

    def test_cli_command(self):
        assert CodexCLIAdapter.cli_command == "codex"

    def test_api_key(self):
        assert CodexCLIAdapter.api_key_env_var == "OPENAI_API_KEY"

    def test_build_command(self):
        adapter = CodexCLIAdapter()
        cmd = adapter._build_command("Edit file")
        assert cmd == ["codex", "--quiet", "--auto-edit", "Edit file"]
