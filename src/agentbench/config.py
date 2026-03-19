"""Centralized configuration for AgentBench-Live."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class EvalSettings:
    """Evaluation-related configuration."""

    pass_threshold: float = 0.8
    auto_weight: float = 0.6
    judge_weight: float = 0.4
    judge_fallback_score: float = 0.7
    output_min_length: int = 100
    file_content_cap: int = 5000
    agent_output_cap: int = 3000
    judge_max_tokens: int = 1024


@dataclass
class BenchmarkConfig:
    """Top-level benchmark configuration."""

    default_trials: int = 3
    install_timeout: int = 120
    eval: EvalSettings = field(default_factory=EvalSettings)
    tasks_dir: str = "tasks"
    results_dir: str = "results"


def load_config(config_path: Path | None = None) -> BenchmarkConfig:
    """Load config from agentbench.yaml with environment variable overrides.

    Precedence: env vars > yaml file > defaults.
    """
    cfg = BenchmarkConfig()

    # Load from YAML if available
    if config_path is None:
        config_path = Path("agentbench.yaml")
    if config_path.exists():
        with open(config_path) as f:
            data = yaml.safe_load(f) or {}
        _apply_yaml(cfg, data)

    # Environment variable overrides
    _apply_env(cfg)

    return cfg


def _apply_yaml(cfg: BenchmarkConfig, data: dict) -> None:
    """Apply YAML data to config."""
    if "default_trials" in data:
        cfg.default_trials = int(data["default_trials"])
    if "install_timeout" in data:
        cfg.install_timeout = int(data["install_timeout"])
    if "tasks_dir" in data:
        cfg.tasks_dir = data["tasks_dir"]
    if "results_dir" in data:
        cfg.results_dir = data["results_dir"]

    eval_data = data.get("eval", {})
    for key in (
        "pass_threshold", "auto_weight", "judge_weight", "judge_fallback_score",
        "output_min_length", "file_content_cap", "agent_output_cap", "judge_max_tokens",
    ):
        if key in eval_data:
            val = eval_data[key]
            setattr(cfg.eval, key, type(getattr(cfg.eval, key))(val))


def _apply_env(cfg: BenchmarkConfig) -> None:
    """Apply environment variable overrides (AGENTBENCH_ prefix)."""
    env_map = {
        "AGENTBENCH_DEFAULT_TRIALS": ("default_trials", int),
        "AGENTBENCH_INSTALL_TIMEOUT": ("install_timeout", int),
        "AGENTBENCH_PASS_THRESHOLD": ("eval.pass_threshold", float),
        "AGENTBENCH_AUTO_WEIGHT": ("eval.auto_weight", float),
        "AGENTBENCH_JUDGE_WEIGHT": ("eval.judge_weight", float),
        "AGENTBENCH_JUDGE_FALLBACK_SCORE": ("eval.judge_fallback_score", float),
        "AGENTBENCH_JUDGE_MAX_TOKENS": ("eval.judge_max_tokens", int),
    }
    for env_key, (path, type_fn) in env_map.items():
        val = os.environ.get(env_key)
        if val is not None:
            parts = path.split(".")
            obj = cfg
            for part in parts[:-1]:
                obj = getattr(obj, part)
            setattr(obj, parts[-1], type_fn(val))
