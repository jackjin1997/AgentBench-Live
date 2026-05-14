#!/usr/bin/env bash
# scripts/track_launch.sh
#
# Background tracker for launch day. Polls GitHub repo metrics every
# INTERVAL seconds, appends to docs/launch-tracker.json, prints a
# human-readable line each tick.
#
# Why: HN/Reddit/Twitter front-page momentum decays in hours. Knowing
# stars-per-hour velocity in real time tells you when to push more
# (still climbing) vs. when to stop spamming (saturated / decaying).
#
# Usage:
#   ./scripts/track_launch.sh                  # default 300s interval
#   INTERVAL=120 ./scripts/track_launch.sh     # poll every 2 min
#   ./scripts/track_launch.sh > tracker.log &  # background, log to file
#
# Stop with Ctrl+C. Data persists in docs/launch-tracker.json.

set -euo pipefail

REPO="${REPO:-jackjin1997/AgentBench-Live}"
INTERVAL="${INTERVAL:-300}"
OUT="docs/launch-tracker.json"

if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: 'gh' CLI required. Install: brew install gh" >&2
  exit 1
fi
if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: 'jq' required. Install: brew install jq" >&2
  exit 1
fi

mkdir -p "$(dirname "$OUT")"
[ -f "$OUT" ] || echo '{"repo":"'"$REPO"'","ticks":[]}' > "$OUT"

PREV_STARS=$(jq -r '.ticks[-1].stars // 0' "$OUT" 2>/dev/null || echo 0)
START_TS=$(date +%s)
START_STARS="$PREV_STARS"

printf "tracking %s every %ds → %s\n" "$REPO" "$INTERVAL" "$OUT"
printf "press Ctrl+C to stop\n\n"
printf "%-20s %8s %8s %8s %8s %s\n" "time" "stars" "Δ" "forks" "issues" "stars/hr"

while true; do
  TICK=$(gh api "/repos/$REPO" --jq '{
    timestamp: (now | todate),
    stars: .stargazers_count,
    forks: .forks_count,
    open_issues: .open_issues_count,
    subscribers: .subscribers_count
  }')

  STARS=$(echo "$TICK" | jq '.stars')
  FORKS=$(echo "$TICK" | jq '.forks')
  ISSUES=$(echo "$TICK" | jq '.open_issues')
  TS_ISO=$(echo "$TICK" | jq -r '.timestamp')

  DELTA=$((STARS - PREV_STARS))
  ELAPSED_HR=$(awk "BEGIN { print ($(date +%s) - $START_TS) / 3600 }")
  if awk "BEGIN { exit ($ELAPSED_HR > 0.01) ? 0 : 1 }"; then
    VELOCITY=$(awk "BEGIN { printf \"%.1f\", ($STARS - $START_STARS) / $ELAPSED_HR }")
  else
    VELOCITY="—"
  fi

  printf "%-20s %8d %+8d %8d %8d %8s\n" "${TS_ISO:0:19}" "$STARS" "$DELTA" "$FORKS" "$ISSUES" "$VELOCITY"

  # Append tick to JSON file
  TMPFILE=$(mktemp)
  jq --argjson tick "$TICK" '.ticks += [$tick]' "$OUT" > "$TMPFILE" && mv "$TMPFILE" "$OUT"

  PREV_STARS=$STARS

  # Trending heuristic: 50+ stars/hr sustained for 2h → likely on daily trending
  if [[ "$VELOCITY" != "—" ]] && awk "BEGIN { exit ($VELOCITY >= 50) ? 0 : 1 }"; then
    printf "  %s stars/hr — pace consistent with GitHub Trending. Don't stop replying.\n" "$VELOCITY"
  fi

  sleep "$INTERVAL"
done
