"""Task schema definition and validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml


class Domain(str, Enum):
    CODE = "code"
    RESEARCH = "research"
    DATA = "data"
    TOOL_USE = "tool-use"
    MULTI_STEP = "multi-step"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class EvalType(str, Enum):
    AUTO = "auto"
    LLM_JUDGE = "llm-judge"
    HUMAN = "human"
    COMPOSITE = "composite"


@dataclass
class SetupConfig:
    base_image: str = "python:3.12-slim"
    files: list[dict[str, str]] = field(default_factory=list)
    install: str = ""
    network: bool = False


@dataclass
class AutoEvalConfig:
    command: str = ""
    pass_threshold: float = 1.0


@dataclass
class LLMJudgeConfig:
    rubric: str = ""
    reference_answer: str = ""
    model: str = "claude-sonnet-4-6"


@dataclass
class EvalConfig:
    type: EvalType = EvalType.AUTO
    auto: AutoEvalConfig | None = None
    llm_judge: LLMJudgeConfig | None = None
    timeout_seconds: int = 300


@dataclass
class Task:
    id: str
    version: int
    domain: Domain
    difficulty: Difficulty
    title: str
    description: str
    human_time_minutes: int
    setup: SetupConfig
    prompt: str
    evaluation: EvalConfig
    tags: list[str] = field(default_factory=list)
    created: str = ""
    author: str = ""


def load_task(path: Path) -> Task:
    """Load and validate a task from a YAML file."""
    with open(path) as f:
        data = yaml.safe_load(f)

    setup_data = data.get("setup", {})
    setup = SetupConfig(
        base_image=setup_data.get("base_image", "python:3.12-slim"),
        files=setup_data.get("files", []),
        install=setup_data.get("install", ""),
        network=setup_data.get("network", False),
    )

    eval_data = data.get("evaluation", {})
    auto_data = eval_data.get("auto")
    auto = AutoEvalConfig(**auto_data) if auto_data else None
    judge_data = eval_data.get("llm_judge")
    judge = LLMJudgeConfig(**judge_data) if judge_data else None

    evaluation = EvalConfig(
        type=EvalType(eval_data.get("type", "auto")),
        auto=auto,
        llm_judge=judge,
        timeout_seconds=eval_data.get("timeout_seconds", 300),
    )

    return Task(
        id=data["id"],
        version=data.get("version", 1),
        domain=Domain(data["domain"]),
        difficulty=Difficulty(data["difficulty"]),
        title=data["title"],
        description=data["description"],
        human_time_minutes=data.get("human_time_minutes", 10),
        setup=setup,
        prompt=data["prompt"],
        evaluation=evaluation,
        tags=data.get("tags", []),
        created=data.get("created", ""),
        author=data.get("author", ""),
    )


def load_all_tasks(tasks_dir: Path) -> list[Task]:
    """Load all tasks from the tasks directory."""
    tasks = []
    for yaml_file in sorted(tasks_dir.rglob("*.yaml")):
        tasks.append(load_task(yaml_file))
    return tasks
