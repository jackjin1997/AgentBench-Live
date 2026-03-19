"""Tests for social card generator."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


SAMPLE_RESULTS = {
    "updated_at": "2026-03-15",
    "benchmark_version": "0.1.0",
    "tasks_count": 10,
    "trials_per_task": 1,
    "agents": [
        {
            "rank": 1,
            "name": "Claude Code",
            "slug": "claude-code",
            "overall_score": 0.744,
            "pass_rate": 0.5,
            "domains": {
                "code": {"score": 1.0, "pass_rate": 1.0},
                "data": {"score": 0.79, "pass_rate": 0.5},
                "multi_step": {"score": 0.88, "pass_rate": 1.0},
                "research": {"score": 0.7, "pass_rate": 0.0},
                "tool_use": {"score": 0.35, "pass_rate": 0.0},
            },
            "tasks": [],
        },
        {
            "rank": 2,
            "name": "Gemini CLI",
            "slug": "gemini-cli",
            "overall_score": 0.516,
            "pass_rate": 0.3,
            "domains": {
                "code": {"score": 1.0, "pass_rate": 1.0},
                "data": {"score": 0.49, "pass_rate": 0.0},
                "multi_step": {"score": 0.74, "pass_rate": 0.5},
                "research": {"score": 0.35, "pass_rate": 0.0},
                "tool_use": {"score": 0.0, "pass_rate": 0.0},
            },
            "tasks": [],
        },
    ],
}


@pytest.fixture
def results_file(tmp_path):
    """Create a temporary results JSON file."""
    path = tmp_path / "results.json"
    path.write_text(json.dumps(SAMPLE_RESULTS))
    return path


@pytest.fixture
def empty_results_file(tmp_path):
    """Create a results file with no agents."""
    path = tmp_path / "empty_results.json"
    path.write_text(json.dumps({"agents": []}))
    return path


class TestGenerateSocialCard:
    def test_creates_png_file(self, results_file, tmp_path):
        """Test that generate_social_card creates a PNG file."""
        from agentbench.social_card import generate_social_card

        output = tmp_path / "card.png"
        result = generate_social_card(results_file, output)

        assert result == output
        assert output.exists()
        # Check PNG magic bytes
        with open(output, "rb") as f:
            header = f.read(8)
        assert header[:4] == b"\x89PNG"

    def test_with_empty_results(self, empty_results_file, tmp_path):
        """Test that an empty results file still produces a valid PNG."""
        from agentbench.social_card import generate_social_card

        output = tmp_path / "empty_card.png"
        result = generate_social_card(empty_results_file, output)

        assert result == output
        assert output.exists()
        with open(output, "rb") as f:
            header = f.read(8)
        assert header[:4] == b"\x89PNG"

    def test_with_agent_filter(self, results_file, tmp_path):
        """Test filtering to specific agents."""
        from agentbench.social_card import generate_social_card

        output = tmp_path / "filtered_card.png"
        result = generate_social_card(results_file, output, agents=["claude-code"])

        assert result == output
        assert output.exists()
        with open(output, "rb") as f:
            header = f.read(8)
        assert header[:4] == b"\x89PNG"

    def test_with_nonexistent_agent_filter(self, results_file, tmp_path):
        """Test filtering to an agent slug that doesn't exist produces a card."""
        from agentbench.social_card import generate_social_card

        output = tmp_path / "no_match.png"
        result = generate_social_card(results_file, output, agents=["nonexistent"])

        assert result == output
        assert output.exists()

    def test_output_path_returned_as_path(self, results_file, tmp_path):
        """Test that the return value is a Path object."""
        from agentbench.social_card import generate_social_card

        output = tmp_path / "card.png"
        result = generate_social_card(results_file, str(output))
        assert isinstance(result, Path)

    def test_missing_results_file_raises(self, tmp_path):
        """Test that a missing results file raises FileNotFoundError."""
        from agentbench.social_card import generate_social_card

        with pytest.raises(FileNotFoundError):
            generate_social_card(tmp_path / "missing.json", tmp_path / "out.png")
