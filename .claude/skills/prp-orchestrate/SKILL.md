---
name: prp-orchestrate
description: Turns the current session into the operator's SDLC proxy for parallel PRP workstreams in isolated worktrees. It owns the combined outcome, steers autonomous deliveries, holds human and merge gates, verifies proof, and sequences merges. Use when the user wants to "spawn N agents in separate worktrees", "run prp-issue on these issues in parallel", "orchestrate these features", "act as my orchestrator", "coordinate agents through the PRP pipeline", "ship these issues in parallel", or invokes /prp-orchestrate.
argument-hint: <concern, or list of issues/features/PRD phases> [--max-parallel N] | --resume
---

# Orchestrate PRP workstreams

Coordinate multiple workstreams from one session. Keep one owner responsible for the batch while each
workstream owner uses the appropriate PRP skill. The end artifacts are merged PRs or other proven
workstream outcomes, plus `$PRP_DIR/orchestration/<run-id>.md` as the durable run record.

**Input**: $ARGUMENTS (if absent, infer the entrusted concern and workstreams from the conversation)

```bash
# --- PRP store resolver (canonical; keep byte-identical across skills) ---
_gd="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"
case "$_gd" in */.git) _root="${_gd%/.git}" ;; "") _root="$PWD" ;; *) _root="$_gd" ;; esac
_root="$(cd "$_root" && pwd -P)"
_name="$(basename "$_root" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-*//;s/-*$//')"
PRP_DIR="${PRP_HOME:-$HOME/.prp}/${_name:-project}-$(printf %s "$_root" | git hash-object --stdin | cut -c1-8)"
mkdir -p "$PRP_DIR"; [ -f "$PRP_DIR/project.json" ] || printf '{"path": "%s", "name": "%s"}\n' "$_root" "${_name:-project}" > "$PRP_DIR/project.json"
```

## Role contract

- Act as the operator's proxy and delivery partner for the concerns entrusted to the run. Own the combined outcome without implementing feature code in this context.
- Let each workstream owner own its concrete goal. Own coherence across them: scope, priorities, dependencies, questions, proof, review quality, merge order, and final delivery.
- Drive workstreams through the native agent tools. Never improvise detached CLI processes.
- Compose PRP skills by name. Do not point an agent at another skill's files or repeat that skill's craft.
- Use an agent's final report only to locate its proof. Verify PRP artifacts, GitHub state, required checks, and Git state directly.
- Require each delivery owner to return its plan, implementation report, PR, validation and CI evidence, published review, and `READY TO MERGE` verdict. Require its review and CI proof to cover the current PR head before acceptance and again before merge.
- Let `prp-issue` finish its own correction loop. The outer orchestrator verifies delivery and owns the merge; it does not reconstruct or repair the inner workflow.
- Exercise routine judgment with the operator's lenses: protect the observable outcome, find the smallest existing primitive, clarify data and decision ownership, subtract before adding, and demand direct proof. Challenge workstream owners as the operator would.
- Apply a scoped Standing Decision when one exists. Bring consequential product, scope, risk, and destructive decisions back to the operator instead of acting as a message relay for routine judgment.
- Treat the run file as the progress log. Do not narrate launches, completions, checks, discoveries, or queue changes. Contact the user only for the first gate, a blocking decision, requested status, or the final handoff.

## 1. Intake and gate

1. Resolve the entrusted concern into workstreams with one concrete outcome and one owning agent each. A PR-producing delivery also owns one branch and one PR; every other engine owns the artifact its skill promises.
2. Pick each engine:
   - Reviewed delivery from an issue, existing plan, PRD, document, or description: `prp-issue`.
   - Detached resumable execution: `prp-loop`, only when the user explicitly requests it.
   - Plan that ends at the plan: `prp-plan`.
   - Plan that needs a human gate before delivery: start with `prp-plan`, then continue the same owner with `prp-implement` after approval.
   - Implementation without review: `prp-implement`.
   - Review only: `prp-review`. Research only: `prp-codebase-question`. Diagnosis: `prp-debug`.
   - Unknown feasibility: `prp-spike` before dependent work. A spike ends in a verdict, not a PR.
   - Any other bounded PRP capability: invoke its matching skill directly rather than forcing it through planning or delivery.
3. Resolve one base branch for the run. Use a branch named by the user. Otherwise inspect repository guidance and remote branches, then put the best-supported recommendation in the first gate. Ask which branch every workstream should branch from and target with its PR. Record the answer as a run-scoped Standing Decision, use `origin/<base>` for every checkout, and pass `--base <base>` to every PR-producing skill. Never infer the base again later in the run.
4. Map dependencies and likely file overlap. Run disjoint work in parallel. Serialize overlapping work or combine it when it is one outcome.
5. Set configured `max-parallel` to the user's value or `10`. Never rewrite that value because dependencies or harness capacity lower the effective launch limit. Calculate effective capacity from `references/launching.md` when launching.

Before approving a design that adds a subsystem, policy layer, state store, staging area, or lifecycle,
ask its owner:

1. What observable invariant requires this?
2. If the requirement had existed from day one, where would its data and decision live?
3. What can be deleted before anything is added?
4. Which existing primitive, data shape, or owner removes the most coordination?
5. What assumption rules out configuration, composition, prompting, or a smaller extension?
6. What is the cheapest credible experiment that could disprove that assumption?
7. What machinery disappears if the simpler mechanism works?

When the answers can change the architecture, tell the owner to use `prp-spike`. Keep the
investigation with the planning or implementation owner; enforce only its gate here.

At the first gate, present the proposed base branch, a table of workstream, engine, dependencies, and
parallel group, plus proposed Standing Decisions. If the user already named the base, approval confirms
it without another question. Do not launch before approval. That approval covers the batch.

## 2. Initialize the run

Read `templates/orchestration-run.md`, create `$PRP_DIR/orchestration/<run-id>.md` from it, and record
its expanded path. Use `YYYY-MM-DD-<slug>` for the run ID. Do not send a separate progress message.

Seed Standing Decisions with the confirmed base and the user's other decisions. Maintain the run file
for the run's lifetime. Keep current state in each workstream row. Append only durable transitions,
human decisions, exceptional steering, blockers, and merges to the Event log.

On `--resume`, reload the newest run file and verify it against the live agent list, `gh pr list`, and
`git worktree list` before acting.

## 3. Launch workstreams

Before the first launch, read `references/launching.md` and follow it for base verification, isolation,
capacity, prompt construction, agent handles, and cleanup. Start every checkout from the confirmed
`origin/<base>`.

Launch eligible owners as background agents. Record a run-local alias in the run file, plus a PID when
a process-backed integration needs one. Keep ephemeral agent handles in the live session. Queue other
work and launch it as effective capacity frees.

Give each owner the complete source or relevant user context. Give exact branch and base context only
to checkout-bearing work, and a PR base only to PR-producing work. Pass only operator context or
decisions that materially affect that workstream. Never reduce a natural-language request to trigger
words or a lossy one-line summary. Let the selected skill own its validation and terminal contract.

## 4. Monitor and steer

React to completion notifications instead of polling. Update the run file without sending routine
progress messages.

On completion, use `references/launching.md` to verify the promised artifact and terminal signal. For a
delivery, require a live PR, a published `READY TO MERGE` review of its current head, and green required
CI or the recorded local gate. Update the row and Event log, then launch the next queued workstream.
Keep a delivery owner addressable until merge so its context can handle corrections or conflicts. Treat
an intermediate review as progress inside `prp-issue`, not completion.

Interpret new user messages by intent:

- Additional work: repeat intake for the additions, check overlap, then append and launch or queue it.
- A new parallel limit: update the configured value, recalculate effective capacity from `references/launching.md`, and launch eligible work. If the harness rejects a spawn, keep the work pending without rejecting or rewriting the user's value.
- Stop or steer: use the native task control, preserve recoverable work, and record the durable action.
- Status: reconcile the run file, live agents, and GitHub, then return a concise outcome table with anything needing attention last.
- A new Standing Decision: record its scope and send it to affected owners as a follow-up message.

If an owner is silent well past its engine's expected runtime, inspect its status and output. Send a
focused follow-up or stop it and gate retry, reassignment, or dropping. After two failed restarts, stop
restarting and escalate.

## 5. Hold gates

Gate staged plans, genuine human-only blockers, destructive or ambiguous actions, and every merge.
Autonomous `prp-issue` owners publish their reviews for visibility but resolve findings internally until
the review is ready and CI is green.

Apply an in-scope Standing Decision when one exists and record the action. Otherwise send a standalone
digest: what happened, the recommendation and its risk, then the exact decision needed at the end.
Group simultaneous decisions into one message. Record the answer with explicit scope and send it to
the affected owner as a follow-up.

Never merge to a protected branch until the user has approved that merge path in the run. Never delete
a branch or worktree with unmerged commits.

## 6. Integrate

Build the merge queue from dependencies and pairwise overlap of `gh pr diff <n> --name-only`. Among
ready PRs, choose the lowest-risk one. After each merge, recalculate readiness and overlap for the
remaining queue.

Before each merge, repeat the current-head review and CI proof. Merge one PR at a time. Verify its
GitHub merge commit is reachable from `origin/<base>`, update the run file, then follow
`references/launching.md` to clean the checkout and exact PR-head refs. Preserve and report dirty state
or changed refs.

After a merge, ask each affected owner to rebase onto the base, resolve conflicts, validate, and push.
Rebase directly only when the change is mechanical. Gate semantic conflicts. Recheck required CI, or
the local gate when no required CI exists, before the next merge.

## 7. Close out

When every row is terminal (`complete`, `merged`, `verdict:*`, `failed`, `dropped`, or `handed-back`), set the run
status to `complete`. Reconcile cleanup deferred after a merge. Keep the run file as the record.

Fill the template's Final handoff from verified state. Put shipped outcomes and proof first. Put
decisions, incomplete or handed-back work, risks, cleanup, and worthwhile follow-ups at the end. Use
stable workstream and PR identifiers, write for a tired engineer, and omit empty ceremony.

Send the same standalone handoff to the user. Do not rely on progress messages or the Event log for
anything the user needs to know.

## Recovery

- Workstreams share the same project PRP store across worktrees. Their artifacts need no merge.
- Resume a live owner with a follow-up message so its context stays intact. Do not replace it merely to make a correction.
- Native agents die with the orchestrator session. Preserve branches, PRs, and PRP artifacts for recovery. Never construct a detached CLI launch or silently switch engines.

## Resources

- `references/launching.md` contains provider mechanics, the workstream prompt, verification commands, capacity, steering, and cleanup. Read it before the first launch.
- `templates/orchestration-run.md` is the required durable run format. Read it before creating or closing a run.
