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

| # | Workstream | Engine | Agent | Branch | Status | PR | Last activity |
|---|-----------|--------|-------|--------|--------|----|--------------|
| 1 | {issue #123: title} | prp-deliver | ws1 | fix/issue-123 | running | - | {HH:MM} {event} |

Agent column holds a run-local alias (ws1, ws2, …) — raw agent IDs are session-internal and never written to files; the orchestrator keeps the alias→handle mapping in-conversation. Fallback-lane workstreams record their PID here instead.

Status vocabulary: `pending` (queued, not launched) | `running` | `needs-gate` | `blocked` (draft PR / awaiting decision) | `pr-open` | `merged` | `verdict:<PROVEN\|DISPROVEN\|CONDITIONAL>` | `failed` | `dropped`.

`verdict:*` is the terminal status for a spike workstream — it produces a verdict and no PR, so it never reaches `pr-open` or `merged`, and `dropped` would read as abandoned when a DISPROVEN spike in fact succeeded. Put the report path in the PR column.

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
