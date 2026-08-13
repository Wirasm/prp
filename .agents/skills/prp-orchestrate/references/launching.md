# Launching, Steering & Monitoring Workstreams

Mechanics for running workstreams as native background agents (the default), plus the detached headless fallback. All actions happen from the orchestrator session.

## Launching a workstream agent (default lane)

Spawn via your delegation tool:

**Isolation is the default, and here it is explicit.** Your spawn tool has no isolation parameter, so create the checkout first — use the prp-worktree skill to create the workstream's branch, then pass the agent its absolute path and tell it to work there. Every workstream that touches the working tree gets one — it cannot then collide with the operator's checkout or with another agent. The exception is narrow, and you must be able to name it: a workstream that does not modify the checkout (`prp-codebase-question`, `prp-debug`, `prp-plan`, `prp-prd`) can be a plain background agent. `prp-debug` may publish to GitHub; assign one owning workstream per issue and never race multiple debuggers against the same thread. Launch independent read-only workstreams in a single message so they run concurrently.

- The test is **"does it touch the working tree"**, not "does it open a PR". `prp-review` reads as read-only and is not: it runs `gh pr checkout`, which switches branches in whatever checkout it lands in. Run it in the operator's and you have moved their HEAD out from under them mid-session. It gets a worktree.
- When in doubt, isolate. A worktree costs a few hundred milliseconds and some disk; a workstream that mutates the shared checkout costs the operator their session.
- **PR-producing workstream** — one background agent in its own pre-created worktree. The agent creates its branch, commits, pushes, and opens the PR itself (that is part of its prompt's definition of done).
- Prefer the pack's advisory agents (`code-reviewer`, `codebase-analyst`, …) when one matches the workstream.
- Record the agent ID/name the tool returns — it is the handle for messaging, stopping, and status checks, and goes in the run file's workstream row.
- Respect the run's `--max-parallel`: completion notifications free slots; launch the next queued workstream then.

## Workstream prompt template

A spawned agent inherits nothing from the orchestrator's conversation. The prompt carries everything:

```
Use the <prp-skill> skill to <task, one line>.

Context:
- Target: <issue #N / plan path / feature description>
- Base branch: branch from origin/<base> (not the local <base>, which may be behind).
  Work on <branch>; never commit to <base>.
- Standing decisions that apply to you: <the SD entries scoped to this workstream, verbatim>
- Bootstrap: <what a FRESH checkout needs before it can build — generated files, a
  patch/vendor step, an install. Omit only if a clean clone builds as-is.>
- Validation gate: <the exact command(s)>. Capture each stage's own exit code.
- Known-noisy tests / environment: <named flaky tests and their signature, plus
  "re-run rather than investigate, and do not fix them in your diff">
- Other work in flight: <branches/PRs touching nearby files, and to stay off them>

Definition of done: <PR opened against <base> with validations green / plan file
written / report written>. Carry the burden of proof: return every promised artifact and
authoritative terminal signal, not only a summary. Report the PR number and a 3-line
summary as your final message.

If blocked on a decision only a human can make: STOP and report the blocker precisely
(what you need decided, the options, your recommendation). You will receive the decision
as a follow-up message — continue from where you stopped.
```

The four added lines each replace a failure the orchestrator otherwise pays for once per agent:

- **Bootstrap** — a fresh worktree is not a working checkout wherever a build prerequisite is gitignored (a vendored/patched dependency, a generated file). The agent's first build fails and it debugs the environment instead of the task. Say the step; do not let it be discovered.
- **Validation gate** — naming it stops each agent inventing its own definition of green.
- **Known-noisy tests** — parallel workstreams share one machine, so `--max-parallel` *raises* the odds of load-dependent flakes. An agent that meets one cold will investigate it, and may "fix" it inside an unrelated diff. Name it, give its signature, and say it is not theirs.
- **Other work in flight** — the orchestrator knows the overlap map from Phase 1; the agent knows nothing. Cheap to pass, and it prevents two branches editing one file.

**Worktree location**: if the repo has its own convention (a `.worktrees/` directory, a worktree skill/CLI, existing sibling worktrees), tell the agent to follow it rather than relying on the isolation default. Some projects list, prune or build against their worktrees, and one parked outside that convention is invisible to those tools.

The STOP-and-report clause is the escalation path: the orchestrator gates the blocker, then **message the decision to the same agent** — it continues with full context. Never replace a blocked agent with a fresh one; the fresh one has no history.

## Engines per workstream type

| Workstream           | Prompt core                                                                                                                                              |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Issue / PRD / document / idea | `Use the prp-deliver skill to own <input> autonomously through a published READY TO MERGE review. Return only the reviewed PR or a concrete blocker only a human can resolve.` |
| Existing plan              | `Use the prp-deliver skill to own the plan at <path> autonomously through a published READY TO MERGE review. Return only the reviewed PR or a concrete blocker only a human can resolve.` |
| Detached autonomous work   | `Use the prp-loop skill for: <input>.` (the headless loop owns persisted stage state and bounded review/fix cycles)                                      |
| Plan only (staged)   | `Use the prp-plan skill to create an implementation plan for: <feature>.` — gate the plan, then message the same agent to proceed with prp-implement |
| Feasibility unknown  | `Use the prp-spike skill to settle: <the question>.` — ends in a PROVEN / DISPROVEN / CONDITIONAL verdict and **no PR**; gate the verdict, then launch or drop the workstreams that depended on it |

A spike workstream does not reach Phase 6 — there is nothing to merge. Its terminal status is `verdict: <PROVEN|DISPROVEN|CONDITIONAL>` plus the report path; do not record it as `merged` (false) or `dropped`, which reads as abandoned and inverts the meaning of a successful DISPROVEN. A CONDITIONAL verdict names a constraint, and deciding whether to pay for that change is itself a Phase 5 gate — often the most consequential one in the run.

## Steering, stopping, status

- **Steer / continue**: send a message to the agent ID — mid-run corrections ("also update the docs"), new standing decisions that affect it, gate answers to a blocked agent, post-merge instructions ("rebase onto <base>, resolve, re-run validations, push"). Log every message in the Event Log.
- **Stop**: your harness's stop control against the workstream's agent. Record `dropped` + reason. Worktree and branch survive a stop — the work can be resumed later by a new agent pointed at the branch (tell it what exists and what remains).
- **Status**: the agent list/status controls give live agent state; the run file gives the semantic state (gate history, decisions). Answer "status?" from both, and reconcile with `gh pr list` when they disagree — PR state wins.

## Verifying completion (authority order)

An agent's "done" report is a claim. Verify before marking `pr-open`/`merged`:

```bash
gh pr list --head <branch> --state all --json number,url,isDraft,state   # PR exists, not draft
gh pr checks <number>                                                    # CI state, if any
git log --oneline <base>..<branch> | head -3                             # commits exist
git diff --name-only origin/<base>...origin/<branch>                     # true PR scope (three-dot!)
```

`--state all` is not optional: **`gh pr list` returns only open PRs by default**, so it goes empty — with no error — the moment a PR merges. Omitting it makes the lookup fail for exactly the terminal state it is meant to confirm, and a `merged` workstream reads as "no PR found".

**No CI is not the same as passing CI.** If `gh pr checks` reports nothing (or only a secret scanner), there is no external fact here — run the project's own validation gate against the branch yourself before marking `pr-open`, per the Role contract. Capture each stage's own exit code; a gate piped into `tail`/`head` reports the *pager's* status, so an `&&` chain sails past a failing stage and the run looks green.

Scope-check with the **three-dot** (merge-base) diff only — a two-dot diff false-flags out-of-scope files whenever the agent based its branch on a different tip (local vs origin) than the one being compared, and both choices are legitimate.

Plus artifacts where the engine promises them (plans/reports/reviews under the project's PRP store — shared across all worktrees, so the orchestrator sees workstream artifacts without merging anything).

## Observability hooks (optional)

For runs that need more than notifications + the run file (e.g. a log line or desktop notification whenever any agent stops), wire hooks on the relevant agent-stop events if your harness supports them. This is an extension point, not a requirement.

## Detached fallback (headless CLI)

Use only when work must **survive the orchestrator session** (overnight batches) or run on a **different harness** (Codex-style CLIs). Same protocol — one worktree + branch per workstream, artifacts and PR state as the only truth — but the launch is a detached process:

```bash
# Create the worktree with the prp-worktree skill (its create command prints
# the worktree's absolute path as its final line):
#   $prp-worktree create <branch> --base <base>
WT=<path printed by prp-worktree create>
cd "$WT" && nohup codex exec --dangerously-bypass-approvals-and-sandbox "<workstream prompt>" \
  > /tmp/orchestrator-ws-<slug>.log 2>&1 &
echo $!   # record the PID in the run file (replaces the agent ID)
```

Differences from the default lane: no live steering (course-correct by restarting with feedback: "Continue the work on the current branch. Previous attempt: <state>. Problem: <issue>. <Correction.>"), no completion notifications (poll PR state and artifacts), the blocked-escalation signal is a **draft PR** describing the blocker instead of a stopped agent, and the log is liveness-only (`kill -0 <PID>`, `tail -5 <log>`) — never status truth. On non-Claude harnesses, swap the CLI and its permission flags; if the harness doesn't read `.agents/skills/`, inline the skill's instructions into the prompt.

## Cleanup (Phase 7 only)

Order matters: **worktrees release branches, so worktrees go first.** An agent worktree holds the PR branch checked out — `gh pr merge --delete-branch` fails on the local deletion while it exists, so merge _without_ `--delete-branch` and clean up after: remove worktrees, then local branches (`-d`), then remote branches (`git push origin --delete <branch>`). A worktree locked by a live (resumable) agent stays until the session ends — leave it and only delete the remote branch.

**`git worktree list` tells you which teardown a worktree needs — read the path, not your memory of the run.** Every worktree here was created explicitly, so every one needs explicit teardown — nothing is reclaimed for you. The run file records no isolation column on purpose: the filesystem already answers this, and it keeps answering after a resume or a compaction, when your memory of which lane you launched into is exactly what has gone missing.

Nothing here is auto-removed; pushed branches survive regardless. Tear every worktree down with the same skill — its rails encode the safety order (refuses dirty worktrees and unmerged branch deletion):

```
$prp-worktree remove <branch> --delete-branch    # --force only after investigating what would be lost
```
