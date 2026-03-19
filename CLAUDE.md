# AgentBench-Live

## Project Goal
Get on GitHub Trending. Current: 2 stars. Need: 50-150+ stars/day spike.

## Strategy: Credibility First, Then Ride the Wave
1. Fix trust gaps (Docker sandbox, more agents, real scores)
2. Wait for a major agent launch, benchmark it day-1
3. Coordinated multi-channel social push (Twitter, Reddit, HN, 小红书, V2EX)

## Current Sprint Scope (accepted from CEO review 2026-03-19)
- [x] Docker sandbox (replace tempdir with real isolation)
- [x] Add Codex CLI adapter (already existed)
- [x] Add Aider adapter
- [ ] Re-run ALL agents × ALL tasks with Docker (get real scores) ← USER ACTION NEEDED
- [x] Methodology doc (docs/methodology.md)
- [x] Frontend redesign (radar charts, domain filtering, hero section)
- [x] Social card generator (shareable comparison images)
- [x] Update README for 4 agents

## Deferred (TODOS)
- Agent Output Viewer (show actual agent work per task) — P2
- GitHub Actions automated benchmark CI — P2
- Automated nightly benchmark runs — Phase 2

## Architecture
```
CLI (click) → Runner → Adapter Registry → SandboxFactory
                                            ├── DockerSandbox (primary)
                                            └── LocalSandbox (fallback)
                                         → Evaluator (auto + LLM judge)
                                         → Ranking → Leaderboard (GitHub Pages)
```

## Key Technical Decisions
- 4 agents: Claude Code, Gemini CLI, Codex CLI, Aider
- Docker sandbox with fallback to local tempdir
- SandboxFactory pattern (not inheritance replacement)
- 1 trial for initial run, pass@k requires multiple trials
- Sanitize API keys from logs/output

## Critical Gaps to Fix
1. Docker not available → fall back to LocalSandbox gracefully
2. Agent timeout → record score=0 and continue, don't crash
3. LLM judge failures → fall back to auto-eval, don't crash

## Competitors
- SWE-bench: ~4k stars (academic, GitHub issues)
- PinchBench: ~640 stars (company-backed)
- ai-coding-lang-bench: ~98 stars (language comparison)
- TheAgentCompany: ~659 stars (simulated company)

## Git Conventions
- Never add Co-Authored-By lines to commits
- Commit messages in English
