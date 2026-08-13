---
name: prp-prd-update
description: Maintains PRD implementation-phase status and artifact links. Always use when a PRP workflow records a planned, implemented, or merged phase in its source PRD, when the user asks to update PRD progress, or when the user invokes $prp-prd-update.
---

> **Arguments:** `$ARGUMENTS` (and `$1`, `$2`, ...) refer to the arguments given when this skill was invoked. Take them from the user's request; if absent, infer them from the conversation.

# Update PRD Phase

Maintain one source PRD's implementation lifecycle without changing its requirements or product decisions.

**Arguments:** $ARGUMENTS

## Resolve and verify

Require an explicit stage, PRD path, and phase number. Read the entire PRD and select the phase by its exact number, never by a fuzzy title match. Stop if the phase is missing, duplicated, or the requested transition conflicts with recorded state.

The Implementation Phases table must have `Plan`, `Report`, and `PR` columns. When reading an older PRD, rename `PRP Plan` to `Plan` and add missing columns without losing any row data or changing unrelated content.

## Apply the stage

- `planned` — require the plan file to exist. Set `Status` to `in-progress` and record its absolute path in `Plan`.
- `implemented` — require the plan and report files to exist and verify that the PR URL identifies an open or merged PR for the current repository. Keep `Status` as `in-progress` and record the absolute plan path, absolute report path, and PR URL.
- `merged` — verify through GitHub that the recorded or supplied PR is merged. Set `Status` to `complete` and preserve all artifact links.

Never mark a phase complete merely because implementation passed or a PR exists. Never move status backward, replace a conflicting artifact silently, infer a phase number, or modify another phase. Repeating the same valid update must be harmless.

## Verify and report

Re-read the exact phase row after editing. Confirm its status and links match the requested stage and that the Markdown table remains valid. Return the PRD path, phase number, resulting status, and recorded links. Do not create a separate report artifact.
