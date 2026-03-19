"""Tests for task schema and loading."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentbench.schema import (
    AutoEvalConfig,
    Difficulty,
    Domain,
    EvalConfig,
    EvalType,
    LLMJudgeConfig,
    SetupConfig,
    Task,
    load_all_tasks,
    load_task,
)


class TestEnums:
    def test_domain_values(self):
        assert Domain.CODE == "code"
        assert Domain.RESEARCH == "research"
        assert Domain.DATA == "data"
        assert Domain.TOOL_USE == "tool-use"
        assert Domain.MULTI_STEP == "multi-step"

    def test_difficulty_values(self):
        assert Difficulty.EASY == "easy"
        assert Difficulty.MEDIUM == "medium"
        assert Difficulty.HARD == "hard"

    def test_eval_type_values(self):
        assert EvalType.AUTO == "auto"
        assert EvalType.LLM_JUDGE == "llm-judge"
        assert EvalType.HUMAN == "human"
        assert EvalType.COMPOSITE == "composite"

    def test_domain_from_string(self):
        assert Domain("code") == Domain.CODE
        assert Domain("tool-use") == Domain.TOOL_USE

    def test_invalid_domain(self):
        with pytest.raises(ValueError):
            Domain("invalid")


class TestSetupConfig:
    def test_defaults(self):
        cfg = SetupConfig()
        assert cfg.base_image == "python:3.12-slim"
        assert cfg.files == []
        assert cfg.install == ""
        assert cfg.network is False


class TestAutoEvalConfig:
    def test_defaults(self):
        cfg = AutoEvalConfig()
        assert cfg.command == ""
        assert cfg.pass_threshold == 1.0


class TestLLMJudgeConfig:
    def test_defaults(self):
        cfg = LLMJudgeConfig()
        assert cfg.rubric == ""
        assert cfg.reference_answer == ""
        assert cfg.model == "claude-sonnet-4-6"


class TestEvalConfig:
    def test_defaults(self):
        cfg = EvalConfig()
        assert cfg.type == EvalType.AUTO
        assert cfg.auto is None
        assert cfg.llm_judge is None
        assert cfg.timeout_seconds == 300


class TestTask:
    def test_creation(self, sample_task):
        assert sample_task.id == "test-001"
        assert sample_task.domain == Domain.CODE
        assert sample_task.difficulty == Difficulty.EASY
        assert sample_task.evaluation.type == EvalType.AUTO

    def test_tags_default(self, sample_task):
        assert sample_task.tags == []

    def test_created_default(self, sample_task):
        assert sample_task.created == ""


class TestLoadTask:
    def test_load_valid_yaml(self, tmp_path):
        yaml_content = """
id: test-yaml-001
version: 1
domain: code
difficulty: easy
title: YAML Test
description: A test task from YAML
human_time_minutes: 5
setup:
  files: []
  install: ""
  network: false
prompt: "Fix the bug"
evaluation:
  type: auto
  auto:
    command: "pytest"
    pass_threshold: 1.0
  timeout_seconds: 60
"""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text(yaml_content)
        task = load_task(yaml_file)
        assert task.id == "test-yaml-001"
        assert task.domain == Domain.CODE
        assert task.evaluation.auto.command == "pytest"

    def test_load_minimal_yaml(self, tmp_path):
        yaml_content = """
id: minimal-001
domain: code
difficulty: easy
title: Minimal
description: Minimal task
prompt: "Do something"
"""
        yaml_file = tmp_path / "minimal.yaml"
        yaml_file.write_text(yaml_content)
        task = load_task(yaml_file)
        assert task.id == "minimal-001"
        assert task.version == 1  # default
        assert task.human_time_minutes == 10  # default

    def test_load_composite_yaml(self, tmp_path):
        yaml_content = """
id: composite-001
domain: data
difficulty: medium
title: Composite
description: Composite eval task
prompt: "Analyze data"
evaluation:
  type: composite
  auto:
    command: "pytest"
  llm_judge:
    rubric: "Quality check"
    reference_answer: "Expected output"
  timeout_seconds: 120
"""
        yaml_file = tmp_path / "composite.yaml"
        yaml_file.write_text(yaml_content)
        task = load_task(yaml_file)
        assert task.evaluation.type == EvalType.COMPOSITE
        assert task.evaluation.auto is not None
        assert task.evaluation.llm_judge is not None

    def test_load_with_tags(self, tmp_path):
        yaml_content = """
id: tags-001
domain: code
difficulty: easy
title: Tagged
description: Task with tags
prompt: "Fix it"
tags: ["python", "bug-fix"]
"""
        yaml_file = tmp_path / "tagged.yaml"
        yaml_file.write_text(yaml_content)
        task = load_task(yaml_file)
        assert task.tags == ["python", "bug-fix"]


class TestLoadAllTasks:
    def test_load_from_directory(self, tmp_path):
        for i in range(3):
            yaml_content = f"""
id: batch-{i:03d}
domain: code
difficulty: easy
title: Task {i}
description: Batch task {i}
prompt: "Do task {i}"
"""
            (tmp_path / f"task-{i}.yaml").write_text(yaml_content)

        tasks = load_all_tasks(tmp_path)
        assert len(tasks) == 3
        assert tasks[0].id == "batch-000"

    def test_load_nested_directories(self, tmp_path):
        subdir = tmp_path / "code"
        subdir.mkdir()
        yaml_content = """
id: nested-001
domain: code
difficulty: easy
title: Nested
description: Nested task
prompt: "Fix it"
"""
        (subdir / "task.yaml").write_text(yaml_content)
        tasks = load_all_tasks(tmp_path)
        assert len(tasks) == 1
        assert tasks[0].id == "nested-001"

    def test_load_empty_directory(self, tmp_path):
        tasks = load_all_tasks(tmp_path)
        assert tasks == []
