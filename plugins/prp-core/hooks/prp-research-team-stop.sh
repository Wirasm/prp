#!/bin/bash

# PRP Research Team Stop Hook
# Validates that the research plan output contains all required sections
# Uses a sentinel file to scope: only fires when prp-research-team command ran

set -euo pipefail

# Read hook input from stdin
HOOK_INPUT=$(cat)

# Sentinel file location
SENTINEL_FILE=".claude/prp-research-team.state"

# Check if our command ran (sentinel exists)
if [[ ! -f "$SENTINEL_FILE" ]]; then
  # Not our command - allow exit
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
