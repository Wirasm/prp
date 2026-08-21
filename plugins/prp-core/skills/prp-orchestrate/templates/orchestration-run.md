# Orchestration run: {run-id}

> Maintained by the orchestrator for the run's lifetime. Stored in the project's shared PRP store and
> never committed by a workstream. The tables are current state and are rewritten as the run changes;
> the Event log is append-only history. Resume with `/prp-orchestrate --resume`.

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
When a gate folds work in, adds a workstream, reassigns an owner, or reorders priority, update the row
here and log the change.

Use a run-local alias such as `ws1` for a native agent. Process-backed integrations may record their
PID in the Owner column. Keep ephemeral native agent handles in the live orchestrator session.

Status vocabulary: `pending` | `running` | `needs-gate` | `pr-open` | `complete` | `merged` |
`verdict:<PROVEN\|DISPROVEN\|CONDITIONAL>` | `failed` | `dropped` | `handed-back`.

Use `complete` when a non-PR skill produced its promised artifact and proof. Use `verdict:*` for a
spike and put its report path in PR or artifact. Use `handed-back` when recoverable work is
intentionally returned to the operator without claiming failure or completion.

## Standing decisions

A standing decision is a precomputed answer to a question that will be asked again. The orchestrator
writes these rows, reading the operator's intent from what they actually said rather than waiting for a
rule-shaped sentence. The authority stays the operator's: never record a rule they did not decide, and
never grant the run a permission they did not give. Before adding a row, phrase it as "For the rest of
this run, ..."; when that sentence reads as false or absurd, the answer belongs somewhere else.

| SD | Decision | Scope | Source | At |
|---|---|---|---|---|
| SD-1 | Base branch is `development` | this run | user | {HH:MM} |
| SD-2 | Fix doc-only review findings without asking | delivery workstreams | user | {HH:MM} |

Route the rest by what it is, not by who said it:

- A one-time authorization to perform a named action, such as merging a specific PR or closing one and
  starting over: Event log.
- A change to the workstream set, its scope, its owner, or its priority: the Workstreams table, plus an
  Event log line.
- An answer carrying live status, such as a sign-off with residual work still in flight: Event log.
- An autonomous orchestrator action: Event log, citing the standing decision that allowed it.

When the operator changes a standing answer, rewrite that row in place and keep its number so earlier
citations still resolve, then log the change. Never leave two rows answering the same question.

## Merge queue

| Order | PR | Workstream | Depends on | Overlap risk | Status |
|---|---|---|---|---|---|
| 1 | #{n} | {#} | - | low | pending |

## Event log

Never edit or remove a line here. Add durable transitions, human decisions, exceptional steering,
blockers, merges, and every change to a standing decision. Do not log routine polling, checks, progress
narration, or duplicate the current row state. Every gate answer is logged here, whether or not it also
becomes a standing decision.

- {HH:MM} launched ws1
- {HH:MM} gate: {question} -> {answer}; {action taken}
- {HH:MM} gate: {question} -> {answer}, recorded as SD-{n}
- {HH:MM} gate: {question} -> {answer}; SD-{n} rewritten to {new rule}
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
