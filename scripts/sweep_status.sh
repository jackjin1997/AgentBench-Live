#!/usr/bin/env bash
# scripts/sweep_status.sh
#
# Quick status of the background benchmark sweep.
# Reads /tmp/abl-bench-logs/ and reports per-agent task progress + ETA.
#
# Usage:
#   ./scripts/sweep_status.sh           # one-shot status
#   watch -n 30 ./scripts/sweep_status.sh   # update every 30s

set -euo pipefail

LOG_DIR="${LOG_DIR:-/tmp/abl-bench-logs}"

if [ ! -d "$LOG_DIR" ]; then
  echo "No sweep log dir at $LOG_DIR — sweep was never started or already cleaned."
  exit 0
fi

if [ -t 1 ]; then
  BOLD="\033[1m"; DIM="\033[2m"; GREEN="\033[32m"; YELLOW="\033[33m"; CYAN="\033[36m"; RESET="\033[0m"
else
  BOLD=""; DIM=""; GREEN=""; YELLOW=""; CYAN=""; RESET=""
fi

printf "${BOLD}AgentBench-Live · sweep status${RESET}\n"
printf "${DIM}log dir: %s${RESET}\n\n" "$LOG_DIR"

# Master sweep log
if [ -f "$LOG_DIR/sweep.log" ]; then
  printf "${BOLD}master log:${RESET}\n"
  cat "$LOG_DIR/sweep.log"
  echo ""
fi

# Per-agent progress
for log in "$LOG_DIR"/*.log; do
  name=$(basename "$log" .log)
  [ "$name" = "sweep" ] && continue
  [ ! -f "$log" ] && continue

  size=$(wc -l < "$log" | tr -d ' ')
  last_mod=$(stat -f "%m" "$log" 2>/dev/null || stat -c "%Y" "$log" 2>/dev/null || echo 0)
  now=$(date +%s)
  age_sec=$((now - last_mod))

  # Count completed trials (lines ending with "best: X.XX")
  trials_done=$(grep -cE 'best: [0-9]\.[0-9]{2}$' "$log" 2>/dev/null || echo 0)
  # Total expected: 10 tasks
  # Find current task being worked on
  current_task=$(grep -E '^[a-z]+-[0-9]{3} —' "$log" | tail -1 | awk '{print $1}')
  current_trial=$(grep -E '^  Trial [0-9]+/' "$log" | tail -1 | awk '{print $2}')

  if [ "$age_sec" -lt 60 ]; then
    activity="${GREEN}active${RESET} (${age_sec}s ago)"
  elif [ "$age_sec" -lt 600 ]; then
    activity="${YELLOW}slow${RESET} (${age_sec}s ago — task may be running)"
  else
    activity="${DIM}stale${RESET} (${age_sec}s ago)"
  fi

  printf "${CYAN}%-15s${RESET}  trials_done=%-3s  on=%-12s  trial=%-6s  $activity\n" \
    "$name" "$trials_done" "${current_task:-?}" "${current_trial:-?}"
done

# All done?
if grep -q "ALL DONE" "$LOG_DIR/sweep.log" 2>/dev/null; then
  echo ""
  printf "${GREEN}${BOLD}✓ Sweep complete.${RESET}\n"
  printf "Next: ${BOLD}python scripts/refresh_publication.py --trials 3${RESET}\n"
fi
