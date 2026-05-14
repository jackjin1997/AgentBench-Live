# Roadmap

> Updated: 2026-05-14 · planned versus aspirational, what we're committing to vs. what's on the wishlist.
> The most useful thing you can do is open an issue or PR against any item below.

---

## v0.3 — Variance done right (next 4-6 weeks)

The v0.2 release surfaced run-to-run variance as the headline finding. v0.3 makes it more than a finding — it becomes the structural design.

### Hard commitments

- [ ] **Multi-trial as the default**, not opt-in. `agentbench run` defaults to `--trials 5` unless explicitly set lower for fast iteration.
- [ ] **Variance reporting in `rankings.json`**: every per-domain entry carries `score` (median), `min`, `max`, plus stdev. Frontend renders these as bars instead of points.
- [ ] **Disentangle agent variance from judge variance**: for any LLM-judged task, run the judge K=5 times on the same agent output, take majority. Publish judge variance separately.
- [ ] **Auto-eval task expansion**: add 5+ new pure-pytest tasks across domains so we have variance-free baselines to anchor the LLM-judge-noisy ones.
- [ ] **`agentbench compare`**: a new CLI that takes 2 agents and tells you, per domain, *whether the difference is significant given variance*. ("Claude beats Gemini at Tool Use, gap > variance" vs. "Claude beats Gemini at Multi-Step but the gap is within noise.")

### Soft commitments

- [ ] CI to fail if a PR's adapter changes drop scores by >3σ on tasks with auto-eval.
- [ ] Per-trial cost (token usage) and latency (wall-clock seconds) populated in `EvalScore`. Schema is already in v0.2 (`models.py`); v0.3 wires it to all 4 adapters.
- [ ] Public results database: store raw per-trial scores, not just aggregates, so anyone can re-aggregate with their own filter.

---

## v0.4 — Coverage and credibility (8-12 weeks out)

Once v0.3 lands, the next bottleneck is *what we measure*. The v0.2 task set is too small.

### What's blocking growth

- 10 tasks is enough to detect direction-of-effect but not magnitude.
- All tasks are *single-turn*; agents that excel at iterative refinement don't get credit.
- IDE-embedded agents (Cursor, Windsurf) can't be tested without a CLI shim.
- We don't yet probe agent failure modes systematically (just collect end-to-end scores).

### Targets

- [ ] **30+ tasks** via community contributions. Each new task PR gets reviewed for: deterministic, self-contained, time-calibrated, auto-scorable.
- [ ] **Multi-turn task variant**: tasks that intentionally require 2-3 conversational turns (clarifying questions, follow-up corrections).
- [ ] **CLI shim guide for IDE agents**: a documented pattern for wrapping Cursor/Windsurf/Devin behind a CLI surface so they can be benchmarked.
- [ ] **Failure-mode taxonomy**: classify per-trial failures into agent-error / tool-error / network-timeout / sandbox-error so spread isn't conflated with infra noise.
- [ ] **Cross-language tasks**: current set is Python-heavy. Add Go, Rust, TypeScript, SQL.

---

## v0.5 — Trustworthy comparison (3-6 months out)

By v0.5 we want to be *the* reference an agent vendor cites in its own marketing because the methodology is rigorous enough that they can't dismiss it.

### Big bets

- [ ] **Replication API**: run the *exact same* benchmark version against *exact same* agent version, get a deterministic-modulo-LLM-stochasticity comparison. Pin model versions explicitly.
- [ ] **Bootstrap confidence intervals** on per-domain rankings, not just min/max ranges.
- [ ] **Independent-run protocol**: invite 2-3 third-party teams to run the suite themselves and publish *their* numbers; meta-leaderboard compares cross-replication agreement.
- [ ] **Public dataset of agent transcripts** (with permission), so researchers can study failure patterns without re-running.
- [ ] **Agent-vendor opt-in mode**: vendors can submit canonical CLI invocation flags via PR, and the result page carries an "as recommended by vendor" disclosure.

---

## What we're explicitly NOT doing

Saying no is part of a roadmap.

- **No web UI for running the benchmark.** It's a CLI tool. If you want a UI, fork it.
- **No paid hosting.** The cost of running multi-trial sweeps is real; users run their own. We provide the harness, you provide the API budget.
- **No tracking/telemetry.** We never collect what tasks you run or what results you get.
- **No "agent marketplace".** This is a benchmark, not a directory.
- **No proprietary scoring.** Every score has a deterministic computation in source. If you can't reproduce a score on your machine, that's a bug.
- **No alignment/safety claims.** AgentBench-Live measures task execution, not behavior under adversarial prompts or value alignment. Other benchmarks do that better.

---

## How to influence the roadmap

In rough order of leverage:

1. **PR a new agent adapter.** Adds 1 column to the leaderboard. ~15 lines.
2. **PR a new task.** Adds 1 row × N agents. YAML + fixtures + scoring rule.
3. **Run a multi-trial sweep yourself and post divergent results.** "I got Claude=0.8, you got Claude=0.6 — let's reconcile."
4. **Open an issue with a methodology critique.** Even if we don't agree, we'll respond and update the limitations section if the critique sticks.
5. **Vote on roadmap items.** Reactions on the corresponding GitHub issue (we'll create a tracking issue per item) inform priority.

---

## Versioning notes

- v0.X means breaking changes can happen between minor versions; pin to a tag if you depend on a specific schema.
- v1.0 will be reserved for the first release with frozen `EvalScore` schema, frozen task IDs, and replication protocol guarantees.
