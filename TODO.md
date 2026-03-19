# AgentBench-Live — TODO

## Current Sprint

- [ ] Install Aider CLI + Codex CLI locally
- [ ] Set ANTHROPIC_API_KEY for real LLM Judge scoring
- [ ] Run all 4 agents x 10 tasks with Docker sandbox
- [ ] Update leaderboard data with new scores
- [ ] Update social posting copy with 4-agent results
- [ ] Coordinated social media launch (timing: next major agent release)

## Deferred (P2)

### Agent Output Viewer
Show actual agent output (code, terminal) for each task on the leaderboard website. Lets users see "evidence" behind each score. Depends on: frontend redesign (done), results JSON format.
- Effort: CC ~30min
- Start: Add output capture to results JSON, then render in leaderboard HTML

### GitHub Actions Benchmark CI
Auto-run benchmark when PRs add new agent adapters. Depends on: Docker sandbox (done), community growth.
- Effort: CC ~1h
- Start: Create .github/workflows/benchmark.yml with Docker + agent setup

### Automated Nightly Runs
Schedule benchmark runs nightly to catch agent regressions. Phase 2 — needs CI infrastructure first.

## Social Launch Checklist

### Channels (do all on same day, Tues-Thurs)
- [ ] Twitter/X — comparison tweet with social card image
- [ ] Reddit r/ClaudeAI — benchmark results post
- [ ] Reddit r/MachineLearning — [P] post
- [ ] Hacker News — Show HN post
- [ ] 小红书 — AI Agent 排行榜
- [ ] V2EX — 分享创造节点
- [ ] 即刻 — same as 小红书
- [ ] 微信群 / Telegram — link + one-liner
