---
name: prp-orchestrate
description: Turn the current session into an SDLC orchestrator that coordinates parallel agent sessions running PRP skills across git worktrees - decompose work into workstreams, launch and monitor them, hold review gates as the user's proxy, and sequence merges. Use when the user wants to "spawn N agents in separate worktrees", "run prp-issue on these issues in parallel", "orchestrate these features", "act as my orchestrator", "coordinate agents through the PRP pipeline", "ship these issues in parallel", or invokes /prp-orchestrate.
argument-hint: <goal, or list of issues/features/PRD phases> [--max-parallel N] | --resume
---

# PRP Orchestrate

Coordinate multiple PRP workstreams from one session. The orchestrator is the user's proxy: it decomposes the goal, launches sub-sessions that run PRP skills, watches their artifacts, sits at review gates (deciding autonomously when a standing decision covers it, escalating a digest when it doesn't), and sequences the merges. The end artifacts are merged PRs plus a run file at `.claude/PRPs/orchestration/<run-id>.md` recording every workstream, decision, and merge.

**Input**: $ARGUMENTS (if absent, infer the goal and workstreams from the conversation)

## Role contract

- **Orchestrate, don't implement.** Never write feature code in the orchestrator session — all product changes happen inside workstream sessions. The orchestrator only touches the run file, worktrees/branches, and merge operations.
- **Trust only authoritative signals**: artifacts under each worktree's `.claude/PRPs/`, `gh pr view/checks`, git state, process liveness. Never parse a sub-session transcript to decide status — logs are for liveness and debugging only.
- **The user is the principal.** Every gate decision is either covered by the Standing Decisions log (act, record it as `auto`) or escalated as a short digest (act on the answer, record it). Never guess on destructive or product-shape decisions.
- **Compose skills by name only.** Sub-sessions are told to "use the prp-issue skill on #123", "use the prp-loop skill for <feature>" — never pointed at another skill's files.

## Phase 1 — Intake & decompose

1. Establish the goal and enumerate candidate workstreams: GitHub issues, PRD phases, features, or PRs to review. One workstream = one branch = one PR.
2. Pick each workstream's engine:
   - Issue → `prp-issue` (investigate, then fix)
   - Feature with an existing plan → `prp-implement`
   - Feature from a description → `prp-loop` (fully autonomous plan→implement→pr→review) or staged `prp-plan` then gate then `prp-implement` (when the user should see plans before code)
   - Review-only / research-only → `prp-review` / `prp-codebase-question` (Lane A, no worktree needed)
3. Map dependencies and conflict risk: predict the files each workstream touches (issue labels, plan Context sections, a quick codebase scan). Disjoint → may run in parallel; overlapping → serialize or merge into one workstream.
4. Size the batch. Default `--max-parallel 3`; raise only when workstreams are provably disjoint. More parallel sessions = more merge surface and more gates — justify, don't default to max.

**CHECKPOINT — the first gate.** Present the run plan as a table (workstream, engine, lane, dependencies, parallel group) plus proposed standing decisions. Do not launch anything until the user approves.

## Phase 2 — Initialize the run

1. Read `templates/orchestration-run.md` and create `.claude/PRPs/orchestration/<run-id>.md` from it exactly (run-id: `YYYY-MM-DD-<slug>`).
2. Seed the Standing Decisions log with everything the user has already decided in conversation (scope each decision: which workstreams, which phases).
3. The orchestrator session maintains this file for the run's lifetime — update it at every launch, status change, gate, and merge. On `/prp-orchestrate --resume` (or "resume the run"), reload state from the newest run file and re-verify it against reality (`git worktree list`, `gh pr list`, process liveness) before acting.

## Phase 3 — Launch

Two lanes — choose per workstream:

- **Lane A — in-session subagents** (Claude Code Task/Agent tool): read-only fan-out only — reviews, research, triage, codebase questions. Cheap, parallel, no durability, must never commit.
- **Lane B — detached headless sessions in worktrees**: anything that commits, pushes, or opens a PR. One worktree + one branch per workstream; survives the orchestrator session; resumable.

Before the first launch of a run, read `references/launching.md` for the exact mechanics (worktree setup, launch command with logging, prompt shape, per-harness notes). Then, per workstream: create the worktree, launch, and record branch / worktree path / PID / log path in the run file. Launch only up to `--max-parallel`; queue the rest and launch as slots free up.

## Phase 4 — Monitor

Poll on a cadence proportional to engine runtime (prp-issue fix ≈ tens of minutes). Per running workstream check, in order of authority (exact commands in `references/launching.md` → Monitoring):

1. PR state and CI checks — authoritative for "done" and "blocked"
2. New artifacts in the worktree's `.claude/PRPs/` and new commits on the branch — progress
3. Process liveness, then log tail — for "is it alive/stuck", never for "is it done"

Update the workstream row and append to the Event Log on every observed change. **Stall rule:** no new commit, artifact, or log output for ~15 minutes → inspect the log tail; either restart the workstream with corrective feedback appended to its prompt, or raise it at a gate. A dead process with no PR is a failed workstream: record, decide (retry / reassign / drop) via the gate protocol.

## Phase 5 — Gates

Gate points: after plans land (staged pipelines), when a PR opens, before every merge, and on any destructive or ambiguous call (force-push, dropping a workstream, scope change, API-shape decisions).

Protocol at each gate:

1. Check the Standing Decisions log. If a decision covers this case within its scope → act, and record it in the Event Log as `auto: <action> per SD-<n>`.
2. Otherwise escalate a **digest**, not a dump: what happened (2–3 lines), what needs deciding, the recommendation and its risk. One message per gate batch — group simultaneous gates.
3. Record the user's answer as a new Standing Decision with explicit scope ("this workstream" vs "rest of run"), so the same question is never asked twice.

Hard rules regardless of standing decisions: never merge to a protected branch without the user having approved that merge path at least once this run; never delete a branch or worktree with unmerged commits.

## Phase 6 — Integrate

When PRs are green and gate-approved:

1. Build the merge queue: dependency edges first, then ascending conflict risk — compute pairwise overlap of `gh pr diff <n> --name-only` between open PRs; overlapping pairs merge farthest apart.
2. Merge strictly one at a time. After each merge, update every remaining branch onto the new base — prefer instructing the owning workstream session to rebase and re-validate; rebase directly only for trivial cases. Re-check `gh pr checks` before the next merge.
3. Conflicts during update: mechanical (imports, adjacent lines, lockfiles) → resolve in the workstream and re-run its validations; semantic (both sides changed the same behavior) → gate it with both diffs summarized.

## Phase 7 — Close out

1. All workstreams merged, dropped, or handed back → set run status `complete` in the run file, with a final table of outcomes.
2. Clean up: `git worktree remove` each worktree and delete merged branches — only after verifying the branch is merged. Keep the run file (it is the record).
3. Summarize for the user: what shipped (PR links), what was dropped and why, standing decisions worth promoting into CLAUDE.md or memory.

## Gotchas

- Each worktree checks out its own `.claude/` — skills and configs resolve normally inside it. Workstream artifacts (plans, reports) are committed on the workstream branch and travel with the PR: by design. The **run file exists only in the main checkout** and is never committed by a workstream.
- One `prp-loop` per worktree is safe (its state file is per-checkout); never run two engines in the same worktree.
- Portability: the protocol core (worktree + headless CLI + artifacts + run file) works on any agent harness; Lane A and the specific launch flags are Claude Code-specific — see the per-harness notes in `references/launching.md`.
- Launch prompts must be self-sufficient — follow the prompt shape in `references/launching.md`, including the standing decisions scoped to that workstream.

## Resources

- `references/launching.md` — worktree setup, launch commands with logging, workstream prompt shape, monitoring/cleanup commands, per-harness notes. Read before the first launch of a run.
- `templates/orchestration-run.md` — the run-file format. Read before creating the run file; follow it exactly.
