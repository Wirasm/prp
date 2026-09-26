# Orchestration run: {run-id}

> Maintained by the orchestrator for the run's lifetime. Stored in the project's shared PRP store and
> never committed by a workstream. Standing decisions are rewritten in place; the Event log is
> append-only history. Live state comes from the agents, GitHub, and Git, not from this file. Resume with
> `$prp-orchestrate --resume`.

**Concern**: {plain-language concern or responsibility entrusted to the run}
**Status**: active | complete | abandoned
**Base branch**: {base}
**Max parallel**: {configured N}
**Started**: {YYYY-MM-DD HH:MM}

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
- A change to the workstream set, its scope, its owner, or its priority: Event log.
- An answer carrying live status, such as a sign-off with residual work still in flight: Event log.
- An autonomous orchestrator action: Event log, citing the standing decision that allowed it.

When the operator changes a standing answer, rewrite that row in place and keep its number so earlier
citations still resolve, then log the change. Never leave two rows answering the same question.

## Event log

Never edit or remove a line here. Add durable transitions, human decisions, exceptional steering,
blockers, merges, and every change to a standing decision. Do not log routine polling, checks, or
progress narration. Every gate answer is logged here, whether or not it also becomes a standing decision.
Stamp every line from `date +%H:%M`, and add the date when it changes.

Launch lines name the durable source (an issue, plan, or the natural-language request), the engine, and
the branch, using a run-local alias such as `ws1`. Keep native agent handles in the live session. End
every workstream with one terminal line: `complete`, `merged`, `verdict:<PROVEN|DISPROVEN|CONDITIONAL>`,
`failed`, `dropped`, or `handed-back`, with its PR or artifact. `handed-back` returns recoverable work to
the operator without claiming failure or completion.

- {HH:MM} launched ws1: {issue #123: title}, prp-issue, fix/issue-123
- {HH:MM} gate: {question} -> {answer}; {action taken}
- {HH:MM} gate: {question} -> {answer}, recorded as SD-{n}
- {HH:MM} gate: {question} -> {answer}; SD-{n} rewritten to {new rule}
- {HH:MM} steered ws2: {material instruction}
- {HH:MM} merged PR #{n}; queued ws3 for rebase
- {HH:MM} ws1 merged: PR #{n}

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
