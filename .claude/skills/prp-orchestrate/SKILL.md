---
name: prp-orchestrate
description: Turn the current session into an SDLC orchestrator that coordinates parallel background agents running PRP skills in isolated worktrees - decompose work into workstreams, launch and steer agents with the native agent tools, hold review gates as the user's proxy, and sequence merges. Use when the user wants to "spawn N agents in separate worktrees", "run prp-issue on these issues in parallel", "orchestrate these features", "act as my orchestrator", "coordinate agents through the PRP pipeline", "ship these issues in parallel", or invokes /prp-orchestrate.
argument-hint: <goal, or list of issues/features/PRD phases> [--max-parallel N] | --resume
---

# PRP Orchestrate

Coordinate multiple PRP workstreams from one session. The orchestrator is the user's proxy: it decomposes the goal, launches background agents that run PRP skills, steers them mid-flight, sits at review gates (deciding autonomously when a standing decision covers it, escalating a digest when it doesn't), and sequences the merges. The run is **live and dynamic** — the user can add work, stop work, redirect an agent, or ask for status at any moment, and the orchestrator absorbs it without restarting anything. The end artifacts are merged PRs plus a run file at `.claude/PRPs/orchestration/<run-id>.md` recording every workstream, decision, and merge.

**Input**: $ARGUMENTS (if absent, infer the goal and workstreams from the conversation)

## Role contract

- **Orchestrate, don't implement.** Never write feature code in the orchestrator session — all product changes happen inside workstream agents. The orchestrator only touches the run file, branches/merges, and the agents themselves.
- **Drive everything through the native agent tools** — spawn with the Agent/Task tool (background, worktree isolation), steer and continue with SendMessage, stop with the task-stop tool, check with the task-list/status tools. Shelling out to a headless CLI is the fallback lane, not the default (see `references/launching.md` → Detached fallback).
- **Trust authoritative signals for "done"**: agent completion reports, artifacts under `.claude/PRPs/`, `gh pr view/checks`, git state. An agent saying "done" is a claim; a green PR is a fact.
- **The user is the principal.** Every gate decision is either covered by the Standing Decisions log (act, record it as `auto`) or escalated as a short digest (act on the answer, record it). Never guess on destructive or product-shape decisions.
- **Compose skills by name only.** Agents are told to "use the prp-issue skill on #123", "use the prp-loop skill for <feature>" — never pointed at another skill's files.

## Phase 1 — Intake & decompose

1. Establish the goal and enumerate workstreams: GitHub issues, PRD phases, features, or PRs to review. One workstream = one agent = one branch = one PR.
2. Pick each workstream's engine:
   - Issue → `prp-issue` (investigate, then fix)
   - Feature with an existing plan → `prp-implement` (+ `prp-pr`)
   - Feature from a description → `prp-loop`, or staged `prp-plan` → gate → `prp-implement` when the user should see plans before code
   - Review-only / research-only → `prp-review` / `prp-codebase-question` (plain background agents, no worktree)
3. Map dependencies and conflict risk: predict the files each workstream touches. Disjoint → parallel; overlapping → serialize or merge into one workstream.
4. Size the batch. Default `--max-parallel 3`; raise only when workstreams are provably disjoint. More parallel agents = more merge surface and more gates.

**CHECKPOINT — the first gate.** Present the run plan as a table (workstream, engine, dependencies, parallel group) plus proposed standing decisions. Do not launch until the user approves. Approval of the plan is approval of the batch — individual launches don't re-ask.

## Phase 2 — Initialize the run

1. Read `templates/orchestration-run.md` and create `.claude/PRPs/orchestration/<run-id>.md` from it exactly (run-id: `YYYY-MM-DD-<slug>`).
2. Seed the Standing Decisions log with everything the user has already decided, each with scope.
3. The orchestrator maintains this file for the run's lifetime — update it on every launch, status change, gate, message sent, and merge. On `--resume`, reload the newest run file and re-verify against reality (task list, `gh pr list`, `git worktree list`) before acting.

## Phase 3 — Launch

Launch each workstream as a **background agent** via the Agent/Task tool — see `references/launching.md` for the exact call shape and prompt template (read it before the first launch of a run):

- **PR-producing work** → background agent with **worktree isolation**: the agent gets its own checkout, creates its branch, commits, pushes, opens the PR.
- **Read-only work** (review, research, triage) → plain background agents, several in one message so they run concurrently.
- Record each agent's ID/name and workstream row in the run file at launch. Respect `--max-parallel`: queue the rest, launch as slots free.

Prompts must be self-sufficient (agents inherit nothing from this conversation) and must end with the escalation rule: *if blocked on a decision only a human can make, stop and report the blocker* — the orchestrator relays it to a gate and resumes the same agent via SendMessage with the answer, context intact.

## Phase 4 — Monitor & mid-run control

Monitoring is **event-driven, not polled**: background agents notify on completion, and their final report returns to the orchestrator. Between events, stay responsive to the user — this phase is a loop of reacting to whichever arrives first:

**On agent completion**: verify the claim against authority (PR exists? checks green? artifacts written?), update the workstream row and Event Log, then launch the next queued workstream into the freed slot. A "blocked" report → gate it (Phase 5), then SendMessage the decision back to the same agent to continue.

**On user input at any time** — the run absorbs it live:
- *"also do X, Y"* → run Phase 1 on the additions only (overlap-check against running workstreams), append rows, launch or queue.
- *"stop workstream N"* / *"stop everything"* → stop the task(s), record status `dropped` + reason; the worktree/branch survive for later.
- *"tell agent N to …"* → SendMessage to that agent; log the instruction in the Event Log.
- *"status?"* → answer from the run file + task list; reconcile against `gh pr list` if stale.
- New standing decisions mid-run → record with scope, and SendMessage them to running agents they affect.

**Stall rule**: an agent silent well past its engine's expected runtime → check task status/output; either SendMessage a nudge with corrective context, or stop it and gate the failure (retry / reassign / drop). Two failed restarts → stop restarting, escalate.

## Phase 5 — Gates

Gate points: after plans land (staged pipelines), when a PR opens, before every merge, on every "blocked" report, and on any destructive or ambiguous call.

1. Check the Standing Decisions log. Covered within scope → act, record `auto: <action> per SD-<n>` in the Event Log.
2. Not covered → escalate a **digest**, not a dump: what happened (2–3 lines), what needs deciding, the recommendation and its risk. Group simultaneous gates into one message.
3. Record the user's answer as a new Standing Decision with explicit scope, then convey it — SendMessage to the affected agent(s), or act directly for merge decisions.

Hard rules regardless of standing decisions: never merge to a protected branch without the user having approved that merge path at least once this run; never delete a branch or worktree with unmerged commits.

## Phase 6 — Integrate

When PRs are green and gate-approved:

1. Build the merge queue: dependency edges first, then ascending conflict risk — pairwise overlap of `gh pr diff <n> --name-only`; overlapping pairs merge farthest apart.
2. Merge strictly one at a time. After each merge, bring remaining branches onto the new base — prefer SendMessage to the owning agent ("rebase onto <base>, resolve, re-run validations, push") so its context handles the conflicts; rebase directly only for trivial cases. Re-check `gh pr checks` before the next merge.
3. Conflicts: mechanical → the owning agent resolves and revalidates; semantic (both sides changed the same behavior) → gate it with both diffs summarized.

## Phase 7 — Close out

1. All workstreams merged, dropped, or handed back → set run status `complete` with a final outcomes table.
2. Clean up remaining worktrees/branches only after verifying merges (`references/launching.md` → Cleanup). Keep the run file — it is the record.
3. Summarize: what shipped (PR links), what was dropped and why, standing decisions worth promoting into CLAUDE.md or memory.

## Gotchas

- Worktree-isolated agents each check out their own `.claude/` — skills resolve normally. Workstream artifacts (plans, reports) commit on the workstream branch and travel with the PR: by design. The **run file lives only in the main checkout** and is never committed by a workstream.
- SendMessage continues an agent **with its context intact** — always prefer it over spawning a fresh agent to "fix" a live workstream; a fresh agent has none of the history.
- Agents and tasks die with the orchestrator session. For work that must survive it (overnight runs, other harnesses), use the detached fallback lane in `references/launching.md` — same protocol, headless CLI, artifacts as truth.
- Hooks are the observability extension point (e.g. notify or log on subagent stop); wire them per-project if the run file + notifications aren't enough — not required for the skill to work.

## Resources

- `references/launching.md` — agent-tool call shapes, the workstream prompt template, SendMessage/stop/status patterns, the detached headless fallback, cleanup. Read before the first launch of a run.
- `templates/orchestration-run.md` — the run-file format. Read before creating the run file; follow it exactly.
