#!/bin/bash

# PRP Research Team Stop Hook
# Validates that the research plan output contains all required sections
# Uses a sentinel file to scope: only fires when prp-research-team command ran

set -euo pipefail

# Read hook input from stdin
HOOK_INPUT=$(cat)

# --- PRP store resolver, READ-ONLY variant (hooks must NEVER create a store) ---
# Derivation is identical to the canonical block in artifact-writing skills, but
# without the mkdir/project.json write, and it bails instead of failing.
#
# Why this variant exists: a Stop hook fires on EVERY stop, in whatever directory
# the session happens to be in. The writing resolver therefore minted a store for
# any folder a session ever passed through — vendored dependencies, throwaway
# checkouts, temp dirs — each left holding nothing but a project.json. Only a
# skill that is actually writing an artifact may create a store.
#
# It also bails on an unreadable root: `cd` into a directory deleted mid-session
# (a removed worktree is the common case) used to abort the whole script under
# `set -e`, surfacing as a hook failure with no stderr.
# `|| true` is load-bearing: outside a git repo `git rev-parse` exits 128, and
# under `set -e` that aborted the whole hook on its first line — surfacing as a
# Stop-hook failure with no stderr, on every stop, in any non-repo directory.
_gd="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null || true)"
case "$_gd" in */.git) _root="${_gd%/.git}" ;; "") _root="$PWD" ;; *) _root="$_gd" ;; esac
_root="$(cd "$_root" 2>/dev/null && pwd -P)" || exit 0
[ -n "$_root" ] || exit 0
_name="$(basename "$_root" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-*//;s/-*$//')"
PRP_DIR="${PRP_HOME:-$HOME/.prp}/${_name:-project}-$(printf %s "$_root" | git hash-object --stdin | cut -c1-8)"

# No store means this command never ran here — nothing to validate.
[ -d "$PRP_DIR" ] || exit 0

SENTINEL_FILE="$PRP_DIR/state/prp-research-team.state"

# Check if our command ran (sentinel exists)
if [[ ! -f "$SENTINEL_FILE" ]]; then
  # Not our command - allow exit
  exit 0
fi

# Ignore a stale sentinel (e.g. left behind by a crashed or interrupted session):
# older than 2 hours cannot belong to this stop, so clean it up and allow exit.
SENTINEL_MTIME=$(stat -f %m "$SENTINEL_FILE" 2>/dev/null || stat -c %Y "$SENTINEL_FILE" 2>/dev/null || date +%s)
if (( $(date +%s) - SENTINEL_MTIME > 7200 )); then
  echo "prp-research-team: ignoring stale sentinel (>2h old)." >&2
  rm -f "$SENTINEL_FILE"
  exit 0
fi

# Read the output file path from sentinel
OUTPUT_PATH=$(head -1 "$SENTINEL_FILE" | tr -d '[:space:]')

# Validate output path exists
if [[ -z "$OUTPUT_PATH" ]] || [[ ! -f "$OUTPUT_PATH" ]]; then
  echo "Research plan file not found at: $OUTPUT_PATH" >&2
  echo "The research plan was not generated. Please re-run the command." >&2
  rm -f "$SENTINEL_FILE"
  exit 0
fi

# Required sections that must be present in the research plan
REQUIRED_SECTIONS=(
  "## Research Question"
  "## Research Question Decomposition"
  "## Team Composition"
  "## Research Tasks"
  "## Team Orchestration Guide"
  "## Acceptance Criteria"
)

# Check each required section
MISSING=()
for section in "${REQUIRED_SECTIONS[@]}"; do
  if ! grep -qF "$section" "$OUTPUT_PATH"; then
    MISSING+=("$section")
  fi
done

# All sections present - clean up and allow exit
if [[ ${#MISSING[@]} -eq 0 ]]; then
  rm -f "$SENTINEL_FILE"
  exit 0
fi

# Never block twice in a row - a second Stop while stop_hook_active means the model
# already got one retry; allow it to stop rather than risk an infinite block loop.
STOP_ACTIVE=$(printf '%s' "$HOOK_INPUT" | jq -r '.stop_hook_active // false' 2>/dev/null || echo false)
if [[ "$STOP_ACTIVE" == "true" ]]; then
  echo "prp-research-team: plan still incomplete after retry; allowing stop." >&2
  rm -f "$SENTINEL_FILE"
  exit 0
fi

# Missing sections - block exit with feedback
MISSING_LIST=""
for section in "${MISSING[@]}"; do
  MISSING_LIST="${MISSING_LIST}"$'\n'"- ${section}"
done

FEEDBACK="Research plan is incomplete. Missing required sections:
${MISSING_LIST}

Please add the missing sections to: ${OUTPUT_PATH}

All 6 required sections must be present:
1. ## Research Question
2. ## Research Question Decomposition
3. ## Team Composition
4. ## Research Tasks
5. ## Team Orchestration Guide
6. ## Acceptance Criteria"

jq -n \
  --arg reason "$FEEDBACK" \
  '{
    "decision": "block",
    "reason": $reason
  }'

exit 0
