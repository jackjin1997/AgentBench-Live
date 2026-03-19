"""Tests for configuration system."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from agentbench.config import BenchmarkConfig, EvalSettings, load_config


class TestEvalSettings:
    def test_defaults(self):
        s = EvalSettings()
        assert s.pass_threshold == 0.8
        assert s.auto_weight == 0.6
        assert s.judge_weight == 0.4
        assert s.judge_fallback_score == 0.7
        assert s.output_min_length == 100
        assert s.file_content_cap == 5000
        assert s.agent_output_cap == 3000
        assert s.judge_max_tokens == 1024


class TestBenchmarkConfig:
    def test_defaults(self):
        cfg = BenchmarkConfig()
        assert cfg.default_trials == 3
        assert cfg.install_timeout == 120
        assert cfg.tasks_dir == "tasks"
        assert cfg.results_dir == "results"
        assert isinstance(cfg.eval, EvalSettings)


class TestLoadConfig:
    def test_defaults_no_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = load_config()
        assert cfg.default_trials == 3

    def test_yaml_loading(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        yaml_content = """
default_trials: 5
install_timeout: 300
eval:
  pass_threshold: 0.9
  auto_weight: 0.7
  judge_weight: 0.3
"""
        (tmp_path / "agentbench.yaml").write_text(yaml_content)
        cfg = load_config()
        assert cfg.default_trials == 5
        assert cfg.install_timeout == 300
        assert cfg.eval.pass_threshold == 0.9
        assert cfg.eval.auto_weight == 0.7
        assert cfg.eval.judge_weight == 0.3

    def test_explicit_path(self, tmp_path):
        yaml_content = "default_trials: 7\n"
        config_file = tmp_path / "custom.yaml"
        config_file.write_text(yaml_content)
        cfg = load_config(config_file)
        assert cfg.default_trials == 7

    def test_env_override(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("AGENTBENCH_DEFAULT_TRIALS", "10")
        monkeypatch.setenv("AGENTBENCH_PASS_THRESHOLD", "0.95")
        cfg = load_config()
        assert cfg.default_trials == 10
        assert cfg.eval.pass_threshold == 0.95

    def test_env_overrides_yaml(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "agentbench.yaml").write_text("default_trials: 5\n")
        monkeypatch.setenv("AGENTBENCH_DEFAULT_TRIALS", "10")
        cfg = load_config()
        assert cfg.default_trials == 10  # env wins

    def test_empty_yaml(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "agentbench.yaml").write_text("")
        cfg = load_config()
        assert cfg.default_trials == 3  # defaults
