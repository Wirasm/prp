# Orchestration Run: {run-id}

> Maintained by the orchestrator session for the lifetime of the run — updated at every
> launch, status change, gate, and merge. Lives only in the main checkout; never committed
> by a workstream. Resume with `/prp-orchestrate --resume`.

**Goal**: {one-line goal}
**Status**: active | complete | abandoned
**Base branch**: {base}
**Max parallel**: {N}
**Started**: {YYYY-MM-DD HH:MM}

## Workstreams

| # | Workstream | Engine | Agent ID | Branch | Status | PR | Last activity |
|---|-----------|--------|----------|--------|--------|----|--------------|
| 1 | {issue #123: title} | prp-issue | {agent-id or PID} | fix/issue-123 | running | - | {HH:MM} {event} |

Status vocabulary: `pending` (queued, not launched) | `running` | `needs-gate` | `blocked` (draft PR / awaiting decision) | `pr-open` | `merged` | `failed` | `dropped`.

## Standing Decisions

| SD | Decision | Scope | Source | At |
|----|----------|-------|--------|-----|
| SD-1 | {e.g. "doc-only review findings: fix without asking"} | rest of run | user | {HH:MM} |

Source is always `user` (answered at a gate, or given up front) — only the user creates SDs. Autonomous actions never appear here; they cite an existing SD from the Event Log.

## Merge Queue

| Order | PR | Workstream | Depends on | Overlap risk | Status |
|-------|----|-----------|------------|--------------|--------|
| 1 | #{n} | {#} | - | low | pending |

## Event Log

Append-only; one line per observed change, gate, or action.

- {HH:MM} launched ws-1 (agent {id})
- {HH:MM} sent to ws-2: {instruction}
- {HH:MM} gate: {question} → {answer} (new SD-{n})
- {HH:MM} auto: {action} per SD-{n}
- {HH:MM} merged PR #{n}; rebased ws-{m}
