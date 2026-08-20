# Orchestration run: {run-id}

> Maintained by the orchestrator for the run's lifetime. Stored in the project's shared PRP store and
> never committed by a workstream. Resume with `/prp-orchestrate --resume`.

**Concern**: {plain-language concern or responsibility entrusted to the run}
**Status**: active | complete | abandoned
**Base branch**: {base}
**Max parallel**: {configured N}
**Started**: {YYYY-MM-DD HH:MM}

## Workstreams

| # | Workstream | Engine | Owner | Branch | Status | PR or artifact | Last activity |
|---|---|---|---|---|---|---|---|
| 1 | {issue #123: title} | prp-issue | ws1 | fix/issue-123 | running | - | {HH:MM} {durable event} |

Use the Workstream column as the durable source: an issue or plan identifier, or the relevant
natural-language request when no other source exists. Do not replace it with a lossy private summary.

Use a run-local alias such as `ws1` for a native agent. Process-backed integrations may record their
PID in the Owner column. Keep ephemeral native agent handles in the live orchestrator session.

Status vocabulary: `pending` | `running` | `needs-gate` | `pr-open` | `merged` |
`verdict:<PROVEN\|DISPROVEN\|CONDITIONAL>` | `failed` | `dropped` | `handed-back`.

Use `verdict:*` as the terminal status for a spike and put its report path in PR or artifact. Use
`handed-back` when recoverable work is intentionally returned to the operator without claiming failure
or completion.

## Standing decisions

| SD | Decision | Scope | Source | At |
|---|---|---|---|---|
| SD-1 | Base branch is `development` | this run | user | {HH:MM} |

Only the user creates a Standing Decision, either up front or at a gate. Record autonomous actions in
the Event log by citing the applicable decision.

## Merge queue

| Order | PR | Workstream | Depends on | Overlap risk | Status |
|---|---|---|---|---|---|
| 1 | #{n} | {#} | - | low | pending |

## Event log

Append only durable transitions, human decisions, exceptional steering, blockers, and merges. Do not
log routine polling, checks, progress narration, or duplicate the current row state.

- {HH:MM} launched ws1
- {HH:MM} gate: {question} -> {answer} (new SD-{n})
- {HH:MM} steered ws2: {material instruction}
- {HH:MM} merged PR #{n}; queued ws3 for rebase

## Final handoff

Fill this section at closeout from verified state. Keep it last so a tired engineer can start here.

**Outcome**: {plain-language batch outcome}

| Workstream | Result | PR or artifact | Proof |
|---|---|---|---|
| ws1 | {shipped outcome or terminal result} | {URL or absolute path} | {review, CI, validation, or verdict} |

### Attention

Include only what needs the operator's attention: decisions, incomplete or handed-back work, meaningful
risks, cleanup that remains, and worthwhile follow-ups. Use stable workstream or PR identifiers. If
nothing needs attention, write `Nothing needs operator attention.`
