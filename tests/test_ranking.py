"""Tests for ranking system."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentbench.ranking import export_leaderboard_json, load_rankings


class TestLoadRankings:
    def test_load_from_results(self, sample_results_dir):
        rankings = load_rankings(sample_results_dir)
        assert len(rankings) == 1
        assert rankings[0]["agent"] == "test-agent"
        assert rankings[0]["avg_score"] == 0.9
        assert rankings[0]["runs"] == 1

    def test_multiple_agents(self, tmp_path):
        for agent in ["agent-a", "agent-b"]:
            data = {
                "agent": agent,
                "timestamp": "20260319-120000",
                "scores": [],
                "summary": {
                    "total_tasks": 5,
                    "avg_score": 0.9 if agent == "agent-a" else 0.7,
                    "pass_rate": 0.8 if agent == "agent-a" else 0.6,
                },
            }
            (tmp_path / f"{agent}.json").write_text(json.dumps(data))

        rankings = load_rankings(tmp_path)
        assert len(rankings) == 2
        assert rankings[0]["agent"] == "agent-a"  # Higher score first
        assert rankings[1]["agent"] == "agent-b"

    def test_empty_directory(self, tmp_path):
        rankings = load_rankings(tmp_path)
        assert rankings == []

    def test_nonexistent_directory(self, tmp_path):
        rankings = load_rankings(tmp_path / "nonexistent")
        assert rankings == []

    def test_invalid_json_skipped(self, tmp_path):
        (tmp_path / "bad.json").write_text("not json")
        (tmp_path / "good.json").write_text(json.dumps({
            "agent": "good-agent",
            "summary": {"total_tasks": 1, "avg_score": 0.8, "pass_rate": 1.0},
        }))

        rankings = load_rankings(tmp_path)
        assert len(rankings) == 1
        assert rankings[0]["agent"] == "good-agent"

    def test_missing_keys_skipped(self, tmp_path):
        (tmp_path / "incomplete.json").write_text(json.dumps({"foo": "bar"}))
        rankings = load_rankings(tmp_path)
        assert rankings == []

    def test_multiple_runs_counts(self, tmp_path):
        """Multiple runs for same agent are counted."""
        data1 = {
            "agent": "test-agent",
            "timestamp": "20260318",
            "scores": [],
            "summary": {"total_tasks": 5, "avg_score": 0.5, "pass_rate": 0.4},
        }
        data2 = {
            "agent": "test-agent",
            "timestamp": "20260319",
            "scores": [],
            "summary": {"total_tasks": 5, "avg_score": 0.9, "pass_rate": 0.8},
        }
        (tmp_path / "run1.json").write_text(json.dumps(data1))
        (tmp_path / "run2.json").write_text(json.dumps(data2))

        rankings = load_rankings(tmp_path)
        assert len(rankings) == 1
        assert rankings[0]["runs"] == 2
        # Score is from last loaded (glob order not guaranteed)
        assert rankings[0]["avg_score"] in (0.5, 0.9)


class TestExportLeaderboardJson:
    def test_export(self, sample_results_dir, tmp_path):
        output = tmp_path / "leaderboard.json"
        export_leaderboard_json(sample_results_dir, output)
        assert output.exists()

        data = json.loads(output.read_text())
        assert "rankings" in data
        assert data["total_agents"] == 1

    def test_creates_parent_dirs(self, sample_results_dir, tmp_path):
        output = tmp_path / "nested" / "dir" / "leaderboard.json"
        export_leaderboard_json(sample_results_dir, output)
        assert output.exists()
