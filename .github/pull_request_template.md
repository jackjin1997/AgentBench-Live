<!-- Pick the type that fits your PR. Delete the rest. -->

### What this PR adds

- [ ] New agent adapter (`src/agentbench/adapters/...`)
- [ ] New benchmark task (`tasks/.../...yaml` + fixtures)
- [ ] Evaluator change (heuristics, judge prompt, scoring rule)
- [ ] Sandbox / runner / CLI change
- [ ] Bug fix
- [ ] Documentation only

### Summary

<!-- One sentence. -->

### If adding an agent

- Adapter file: `src/agentbench/adapters/<your_agent>.py`
- Registered in: `src/agentbench/adapters/__init__.py`
- Benchmark results (paste at minimum one trial; ideally 3 for variance):

  ```
  agentbench run --agent <your-agent> --tasks all --trials 3
  # paste the `agentbench leaderboard` output here
  ```

### If adding a task

- Task file: `tasks/<domain>/<task-id>.yaml`
- Fixtures: `tasks/fixtures/<task-id>/`
- Tested against ≥1 existing agent (Claude Code or Gemini CLI) — paste output:

  ```
  agentbench run --agent claude-code --tasks <your-task-id>
  ```

### Tests

- [ ] `pytest` passes locally
- [ ] If touching adapters or evaluator, added/updated unit tests
- [ ] No regression in `coverage` (currently ≈90%)

### Documentation

- [ ] README updated if user-visible behavior changed
- [ ] `docs/methodology.md` updated if scoring rule changed
- [ ] Adapter docstring describes the CLI invocation, env vars, and any quirks

<!--
Optional but appreciated:
- Reference the issue this addresses (`closes #N`)
- Note any tradeoffs or alternatives you considered
- Flag anything you're unsure about and want feedback on
-->
