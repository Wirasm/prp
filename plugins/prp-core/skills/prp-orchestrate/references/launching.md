# Launching, Steering & Monitoring Workstreams

Mechanics for running workstreams as native background agents (the default), plus the detached headless fallback. All actions happen from the orchestrator session.

## Launching a workstream agent (default lane)

Spawn via the Agent/Task tool:

- **PR-producing workstream** — one agent, `run_in_background` (the default), **`isolation: "worktree"`** so the agent works in its own checkout and cannot collide with the main checkout or other agents. The agent creates its branch, commits, pushes, and opens the PR itself (that is part of its prompt's definition of done).
- **Read-only workstream** (review, research, triage) — plain background agents, no isolation needed; launch several in a single message so they run concurrently. Prefer the pack's advisory agents (`prp-core:code-reviewer`, `prp-core:codebase-analyst`, …) when one matches.
- Record the agent ID/name the tool returns — it is the handle for SendMessage, stop, and status, and goes in the run file's workstream row.
- Respect the run's `--max-parallel`: completion notifications free slots; launch the next queued workstream then.

## Workstream prompt template

A spawned agent inherits nothing from the orchestrator's conversation. The prompt carries everything:

```
Use the <prp-skill> skill to <task, one line>.

Context:
- Target: <issue #N / plan path / feature description>
- Base branch: <base>. Create and work on branch <branch>; never commit to <base>.
- Standing decisions that apply to you: <the SD entries scoped to this workstream, verbatim>

Definition of done: <PR opened against <base> with validations green / plan file
written / report written>. Report the PR number and a 3-line summary as your final message.

If blocked on a decision only a human can make: STOP and report the blocker precisely
(what you need decided, the options, your recommendation). You will receive the decision
as a follow-up message — continue from where you stopped.
```

The STOP-and-report clause is the escalation path: the orchestrator gates the blocker, then **SendMessage the decision to the same agent** — it continues with full context. Never replace a blocked agent with a fresh one; the fresh one has no history.

## Engines per workstream type

| Workstream | Prompt core |
|---|---|
| GitHub issue | `Use the prp-issue skill: first investigate #N, then fix #N.` |
| Feature, plan exists | `Use the prp-implement skill to execute the plan at <path>, then use the prp-pr skill to open a PR.` |
| Feature, autonomous | `Use the prp-loop skill for: <feature description>.` (the loop handles plan→implement→pr→review; the orchestrator then only gates the final merge) |
| Plan only (staged) | `Use the prp-plan skill to create an implementation plan for: <feature>.` — gate the plan, then SendMessage the same agent to proceed with prp-implement |

## Steering, stopping, status

- **Steer / continue**: SendMessage to the agent ID — mid-run corrections ("also update the docs"), new standing decisions that affect it, gate answers to a blocked agent, post-merge instructions ("rebase onto <base>, resolve, re-run validations, push"). Log every message in the Event Log.
- **Stop**: the task-stop tool against the workstream's task. Record `dropped` + reason. Worktree and branch survive a stop — the work can be resumed later by a new agent pointed at the branch (tell it what exists and what remains).
- **Status**: the task-list/status tools give live agent state; the run file gives the semantic state (gate history, decisions). Answer "status?" from both, and reconcile with `gh pr list` when they disagree — PR state wins.

## Verifying completion (authority order)

An agent's "done" report is a claim. Verify before marking `pr-open`/`merged`:

```bash
gh pr list --head <branch> --json number,url,isDraft,state   # PR exists, not draft
gh pr checks <number>                                        # CI state
git log --oneline <base>..<branch> | head -3                 # commits exist
```

Plus artifacts where the engine promises them (plans/reports/reviews under the branch's `.claude/PRPs/`).

## Observability hooks (optional)

For runs that need more than notifications + the run file (e.g. a log line or desktop notification whenever any agent stops), wire project hooks on the relevant events (e.g. SubagentStop) in `.claude/settings.json`. This is an extension point, not a requirement — consult the current Claude Code hooks docs for event names and payloads.

## Detached fallback (headless CLI)

Use only when work must **survive the orchestrator session** (overnight batches) or run on a **different harness** (Codex-style CLIs). Same protocol — one worktree + branch per workstream, artifacts and PR state as the only truth — but the launch is a detached process:

```bash
# Create the worktree with the prp-worktree skill (its create command prints
# the worktree's absolute path as its final line):
#   /prp-worktree create <branch> --base <base>
WT=<path printed by prp-worktree create>
cd "$WT" && nohup claude -p "<workstream prompt>" \
  --dangerously-skip-permissions --output-format stream-json --verbose \
  > /tmp/orchestrator-ws-<slug>.log 2>&1 &
echo $!   # record the PID in the run file (replaces the agent ID)
```

Differences from the default lane: no SendMessage (course-correct by restarting with feedback: "Continue the work on the current branch. Previous attempt: <state>. Problem: <issue>. <Correction.>"), no completion notifications (poll PR state and artifacts), the blocked-escalation signal is a **draft PR** describing the blocker instead of a stopped agent, and the log is liveness-only (`kill -0 <PID>`, `tail -5 <log>`) — never status truth. On non-Claude harnesses, swap the CLI and its permission flags; if the harness doesn't read `.claude/skills/`, inline the skill's instructions into the prompt.

## Cleanup (Phase 7 only)

Agent-tool worktrees are auto-removed when unchanged; pushed branches survive regardless. For worktrees created via the prp-worktree skill (fallback lane), tear down with the same skill — its rails encode the safety order (refuses dirty worktrees and unmerged branch deletion):

```
/prp-worktree remove <branch> --delete-branch    # --force only after investigating what would be lost
```
