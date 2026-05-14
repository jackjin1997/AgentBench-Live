#!/usr/bin/env bash
# scripts/start_day2.sh
#
# One-command Day-2 onboarding for the Trending Launch sprint.
# Pre-flight checks every dependency and either runs the multi-trial
# benchmark for all 4 agents, or tells you exactly what's missing.
#
# Idempotent: safe to re-run after fixing a missing dependency.
#
# Usage:
#   ./scripts/start_day2.sh                 # full sweep (default)
#   ./scripts/start_day2.sh --check         # just run preflight, no benchmark
#   ./scripts/start_day2.sh --agent claude-code   # subset
#   TRIALS=5 ./scripts/start_day2.sh        # override trial count

set -euo pipefail

# ---- Style ----
if [ -t 1 ]; then
  BOLD="\033[1m"; DIM="\033[2m"; RED="\033[31m"; GREEN="\033[32m"; YELLOW="\033[33m"; CYAN="\033[36m"; RESET="\033[0m"
else
  BOLD=""; DIM=""; RED=""; GREEN=""; YELLOW=""; CYAN=""; RESET=""
fi

ok()    { printf "  ${GREEN}✓${RESET} %s\n" "$1"; }
warn()  { printf "  ${YELLOW}⚠${RESET} %s\n" "$1"; }
fail()  { printf "  ${RED}✗${RESET} %s\n" "$1"; }
info()  { printf "  ${DIM}·${RESET} %s\n" "$1"; }
hdr()   { printf "\n${BOLD}%s${RESET}\n" "$1"; }

# ---- Args ----
CHECK_ONLY=0
AGENTS_OVERRIDE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --check) CHECK_ONLY=1; shift ;;
    --agent) AGENTS_OVERRIDE="$2"; shift 2 ;;
    -h|--help)
      grep '^# ' "$0" | sed 's/^# \{0,1\}//' | head -20
      exit 0
      ;;
    *) fail "Unknown arg: $1"; exit 2 ;;
  esac
done

TRIALS="${TRIALS:-3}"
PASS=0
SOFT_FAIL=0
HARD_FAIL=0

hdr "AgentBench-Live · Day 2 preflight"
echo "  trials per task: ${BOLD}${TRIALS}${RESET}    (override with TRIALS=5)"

# ---- 1. Python + agentbench installed ----
hdr "[1/5] Python + agentbench package"
if command -v python3 >/dev/null 2>&1; then
  PYV=$(python3 --version 2>&1 | awk '{print $2}')
  ok "python3 ${PYV}"
else
  fail "python3 not found"; HARD_FAIL=$((HARD_FAIL+1))
fi

if python3 -c "import agentbench" 2>/dev/null; then
  ok "agentbench importable"
else
  fail "agentbench not importable. Run: pip install -e ."
  HARD_FAIL=$((HARD_FAIL+1))
fi

# ---- 2. API keys ----
hdr "[2/5] API keys"
if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  ok "ANTHROPIC_API_KEY set ($(echo "$ANTHROPIC_API_KEY" | head -c 12)…)"
else
  fail "ANTHROPIC_API_KEY missing — Claude Code + LLM judge fall back to heuristic"
  info "  export ANTHROPIC_API_KEY=sk-ant-..."
  HARD_FAIL=$((HARD_FAIL+1))
fi

if [ -n "${OPENAI_API_KEY:-}" ]; then
  ok "OPENAI_API_KEY set ($(echo "$OPENAI_API_KEY" | head -c 12)…)"
else
  warn "OPENAI_API_KEY missing — Codex CLI run will fail"
  info "  export OPENAI_API_KEY=sk-..."
  SOFT_FAIL=$((SOFT_FAIL+1))
fi

if [ -n "${GEMINI_API_KEY:-}${GOOGLE_API_KEY:-}" ]; then
  ok "Gemini key set"
else
  warn "GEMINI_API_KEY / GOOGLE_API_KEY missing — Gemini CLI run will fail"
  SOFT_FAIL=$((SOFT_FAIL+1))
fi

# ---- 3. Docker ----
hdr "[3/5] Docker (sandbox)"
if command -v docker >/dev/null 2>&1; then
  if docker info >/dev/null 2>&1; then
    ok "Docker daemon running"
  else
    warn "docker installed but daemon not reachable — will fall back to LocalSandbox (less credible)"
    info "  Open Docker Desktop, wait ~10s, re-run this script"
    SOFT_FAIL=$((SOFT_FAIL+1))
  fi
else
  warn "docker CLI not installed — sandbox falls back to local tempdir"
  SOFT_FAIL=$((SOFT_FAIL+1))
fi

# ---- 4. Agent CLIs ----
# bash 3.2 (macOS default) lacks associative arrays — use case statement.
hdr "[4/5] Agent CLIs"
AVAILABLE_AGENTS=()
agent_cli() {
  case "$1" in
    claude-code) echo claude ;;
    gemini-cli)  echo gemini ;;
    codex-cli)   echo codex ;;
    aider)       echo aider ;;
    *)           echo "" ;;
  esac
}
for a in claude-code gemini-cli codex-cli aider; do
  cli="$(agent_cli "$a")"
  if command -v "$cli" >/dev/null 2>&1; then
    ver=$("$cli" --version 2>&1 | head -1 || echo "?")
    ok "$a → $cli ($ver)"
    AVAILABLE_AGENTS+=("$a")
  else
    warn "$a → '$cli' not on PATH (skip in benchmark)"
    SOFT_FAIL=$((SOFT_FAIL+1))
  fi
done

# ---- 5. Repo state ----
hdr "[5/5] Repo state"
if [ -f docs/data/rankings.json ]; then
  ok "docs/data/rankings.json exists (current narrative will overwrite)"
else
  warn "docs/data/rankings.json missing"
fi

if git diff --quiet 2>/dev/null && git diff --cached --quiet 2>/dev/null; then
  ok "working tree clean"
else
  warn "working tree has uncommitted changes — commit before re-running benchmark"
fi

# ---- Summary ----
hdr "Summary"
if [ $HARD_FAIL -gt 0 ]; then
  printf "  ${RED}✗ %d hard fails — fix above before continuing${RESET}\n" "$HARD_FAIL"
  exit 1
fi
if [ $SOFT_FAIL -gt 0 ]; then
  printf "  ${YELLOW}⚠ %d soft warnings — benchmark will run partial${RESET}\n" "$SOFT_FAIL"
else
  printf "  ${GREEN}✓ all green${RESET}\n"
fi

if [ ${#AVAILABLE_AGENTS[@]} -eq 0 ]; then
  fail "No agents available — install at least one CLI"
  exit 1
fi

if [ $CHECK_ONLY -eq 1 ]; then
  printf "${DIM}--check passed; not running benchmark${RESET}\n"
  exit 0
fi

# ---- Run ----
RUN_AGENTS=("${AVAILABLE_AGENTS[@]}")
if [ -n "$AGENTS_OVERRIDE" ]; then
  RUN_AGENTS=("$AGENTS_OVERRIDE")
fi

hdr "Running benchmark · ${#RUN_AGENTS[@]} agents × 10 tasks × ${TRIALS} trials"
printf "${DIM}Estimated wall time: ~%d-%d minutes (depends on network + agent latency)${RESET}\n" \
  $((${#RUN_AGENTS[@]} * 10 * TRIALS / 4)) $((${#RUN_AGENTS[@]} * 10 * TRIALS / 2))

for a in "${RUN_AGENTS[@]}"; do
  hdr "→ $a"
  agentbench run --agent "$a" --domain all --trials "$TRIALS" || warn "$a run had failures (continuing)"
done

hdr "Done"
ok "Results in results/"
ok "Next: have Claude regenerate docs/data/rankings.json + docs/findings.md from new data"
ok "Then: ./scripts/gen_launch_card.py to refresh the social card"
echo ""
printf "${DIM}Tell Claude: \"benchmark done, polish numbers\"${RESET}\n"
