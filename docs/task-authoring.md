# Task Authoring Guide

This document describes how to create benchmark tasks for AgentBench-Live.

## Task Schema

Each task is a YAML file in the `tasks/` directory, organized by domain.

```yaml
# tasks/<domain>/<task-id>.yaml
id: code-001
version: 1
domain: code          # code | research | data | tool-use | multi-step
difficulty: easy      # easy | medium | hard
title: "Fix off-by-one error in pagination"
description: |
  A concise description of what the agent needs to accomplish.
  Should be clear enough for any agent to understand without ambiguity.

# Time calibration (METR-inspired)
human_time_minutes: 5   # Estimated time for a competent human

# Environment setup
setup:
  base_image: "python:3.12-slim"    # Docker base image
  files:                             # Files to place in the workspace
    - src: "fixtures/code-001/"
      dst: "/workspace/"
  install: |                         # Setup commands
    pip install pytest
  network: false                     # Whether network access is allowed

# The prompt given to the agent
prompt: |
  The file `/workspace/app.py` has a pagination bug. Users report that
  page 2 shows the same results as page 1. Fix the bug.

  Run `pytest /workspace/test_app.py` to verify your fix.

# Evaluation
evaluation:
  type: auto          # auto | llm-judge | human | composite
  auto:
    command: "pytest /workspace/test_app.py -v"
    pass_threshold: 1.0    # Fraction of tests that must pass
  timeout_seconds: 300     # Max execution time

# Metadata
tags: ["pagination", "bug-fix", "python"]
created: "2026-03-14"
author: "agentbench-live"
```

## Domain Guidelines

### Code
- Must include test files for automated verification
- Bug should be reproducible and unambiguous
- Fix should be achievable without external dependencies

### Research
- Use LLM-as-Judge evaluation with rubric
- Define clear criteria: accuracy, completeness, citation quality
- Provide reference answer for judge calibration

### Data
- Include input data files (CSV, JSON)
- Define expected outputs or key insights
- Scoring: accuracy of numerical results + quality of insights

### Tool Use
- Specify which tools/APIs are available
- Network access typically required
- Score: task completion + number of tool calls (efficiency)

### Multi-step
- Combine 2+ domains in a single workflow
- Score: end-to-end completion + intermediate step quality
- Higher timeout (10-30 min)

## Quality Checklist

- [ ] Task is solvable by a competent human in the stated time
- [ ] Success criteria are unambiguous
- [ ] Setup creates a reproducible environment
- [ ] No reliance on external services that may change (for `network: false` tasks)
- [ ] Tested with at least one agent before submission
