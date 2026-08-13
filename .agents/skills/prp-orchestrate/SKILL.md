---
name: prp-orchestrate
description: Turn the current session into an SDLC orchestrator that coordinates parallel background agents running PRP skills in isolated worktrees - decompose work into workstreams, launch and steer background agents with your harness's delegation tools, hold review gates as the user's proxy, and sequence merges. Use when the user wants to "spawn N agents in separate worktrees", "run prp-deliver on these issues in parallel", "orchestrate these features", "act as my orchestrator", "coordinate agents through the PRP pipeline", "ship these issues in parallel", or invokes $prp-orchestrate.
---

> **Arguments:** `$ARGUMENTS` (and `$1`, `$2`, ...) refer to the arguments given when this skill was invoked. Take them from the user's request; if absent, infer them from the conversation.

# PRP Orchestrate

Coordinate multiple PRP workstreams from one session. The orchestrator is the user's proxy: it decomposes the goal, launches background agents that run PRP skills, steers them mid-flight, sits at review gates (deciding autonomously when a standing decision covers it, escalating a digest when it doesn't), and sequences the merges. The run is **live and dynamic** — the user can add work, stop work, redirect an agent, or ask for status at any moment, and the orchestrator absorbs it without restarting anything. The end artifacts are merged PRs plus a run file at `$PRP_DIR/orchestration/<run-id>.md` recording every workstream, decision, and merge.

**Input**: $ARGUMENTS (if absent, infer the goal and workstreams from the conversation)

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

- **Orchestrate, don't implement.** Never write feature code in the orchestrator session — all product changes happen inside workstream agents. The orchestrator only touches the run file, branches/merges, and the agents themselves.
- **Drive everything through your harness's delegation tools** — spawn background workstream agents in isolated worktrees (kild rooms via the kild_* tools, or your subagent mechanism), steer a running agent by sending it a follow-up message, stop it and check status with the matching controls. Shelling out to a headless CLI is the fallback lane, not the default (see `references/launching.md` → Detached fallback).
- **Trust authoritative signals for "done"**: artifacts under the project's PRP store, agent completion reports, `gh pr view/checks`, git state. An agent saying "done" is a claim; a green PR is a fact.
- **Where the project has no CI, there is no fact to trust — so the orchestrator re-runs the gate.** Check once per run whether the repo actually has checks (`gh pr checks <n>`; a secret-scanner alone is not a build). If it does not, a workstream's "validations green" is a self-report, and accepting it makes the orchestrator a relay for whatever the agent believed. Run the project's own gate against the branch before marking `pr-open`. Re-run more than once where the suite has known flakes — one green run does not distinguish a fix from a lucky sample.
- **The user is the principal.** Every gate decision is either covered by the Standing Decisions log (act, record it as `auto`) or escalated as a short digest (act on the answer, record it). Never guess on destructive or product-shape decisions.
- **Compose skills by name only.** Agents are told to "use the prp-deliver skill on #123" or "use the prp-loop skill for detached execution" — never pointed at another skill's files.
- **Think in invariants and primitives.** Do not let a workstream inherit a proposed implementation as its objective. Preserve the required observable outcome, look for the smallest existing primitive that can satisfy it, and prove an uncertain architectural hinge before allowing substantial new machinery.

## Phase 1 — Intake & decompose

1. Establish the goal and enumerate workstreams: GitHub issues, PRD phases, features, or PRs to review. One workstream = one agent = one branch = one PR.
2. Pick each workstream's engine:
   - Issue, existing plan, PRD, document, or description going to a reviewed PR → `prp-deliver`
   - Detached execution that must survive this orchestrator session → `prp-loop`
   - Plan only → `prp-plan`; implementation without review → `prp-implement`
   - Review-only → `prp-review` (worktree — it runs `gh pr checkout`); research-only → `prp-codebase-question` (plain background agent)
   - **Feasibility unknown** — "can this be built here", "what would it cost to allow it" → `prp-spike` (worktree). It ends in a verdict, not a PR; what it gates is whether the downstream workstreams should exist at all, so schedule it *before* the work it informs
3. Map dependencies and conflict risk: predict the files each workstream touches. Disjoint → parallel; overlapping → serialize or merge into one workstream.
4. Size the batch. Default `--max-parallel 3`; raise only when workstreams are provably disjoint. More parallel agents = more merge surface and more gates.

Before approving a plan or implementation shape that adds a subsystem, policy layer, state store, staging area, or lifecycle, probe the owning agent in its existing context:

- What invariant requires this?
- Which existing primitive comes closest?
- What unproven assumption rules out configuration, composition, prompting, or a smaller extension?
- What is the cheapest credible experiment that could disprove that assumption?
- What machinery disappears if the simpler mechanism works?

When those answers can change the architecture, tell the agent to use `prp-spike` before dependent work proceeds. The orchestrator routes and enforces this reasoning; the planning or implementation agent owns the investigation.

**CHECKPOINT — the first gate.** Present the run plan as a table (workstream, engine, dependencies, parallel group) plus proposed standing decisions. Do not launch until the user approves. Approval of the plan is approval of the batch — individual launches don't re-ask.

## Phase 2 — Initialize the run

1. Read `templates/orchestration-run.md`, run `mkdir -p "$PRP_DIR/orchestration"`, and create `$PRP_DIR/orchestration/<run-id>.md` from it exactly (run-id: `YYYY-MM-DD-<slug>`); report the expanded absolute path.
2. Seed the Standing Decisions log with everything the user has already decided, each with scope.
3. The orchestrator maintains this file for the run's lifetime — update it on every launch, status change, gate, message sent, and merge. On `--resume`, reload the newest run file and re-verify against reality (task list, `gh pr list`, `git worktree list`) before acting.

## Phase 3 — Launch

**Pre-flight, before any spawn**: `git fetch`, then reconcile the base with origin in **both directions** — `git rev-list --left-right --count origin/<base>...<base>` must read `0	0`.

```
0	3   → local is AHEAD: 3 unpushed commits. Every PR carries them as phantom scope.
3	0   → local is BEHIND: agents branching from it silently omit 3 merged commits.
```

Worktree agents branch from one tip while PRs diff against the other, and **both directions break that** — but only the ahead case is visible in the PR. A base that is merely behind produces branches that build, test and merge cleanly while missing work that already landed; the cost surfaces later as a conflict, a duplicated fix, or a regression re-introduced. Tell agents the exact ref to branch from (`origin/<base>`, not `<base>`) rather than trusting the local tip.

Launch each workstream as a **background agent** via your delegation tool — see `references/launching.md` for the exact call shape and prompt template (read it before the first launch of a run):

- **Worktree isolation is the default** — every workstream that touches the working tree gets its own checkout. The test is *"does it touch the working tree"*, not *"does it open a PR"*: `prp-review` looks read-only but runs `gh pr checkout`, so it gets a worktree too.
- **PR-producing work** → background agent, worktree-isolated: the agent creates its branch, commits, pushes, opens the PR.
- **Read-only working-tree work** — does not modify the checkout (`prp-codebase-question`, `prp-debug`, `prp-plan`, `prp-prd`) → plain background agents. `prp-debug` may publish to GitHub, so give each issue one owning workstream and do not race multiple debuggers against it.
- Record each agent's ID/name and workstream row in the run file at launch. Respect `--max-parallel`: queue the rest, launch as slots free.

Prompts must be self-sufficient (agents inherit nothing from this conversation) and must end with the escalation rule: *if blocked on a decision only a human can make, stop and report the blocker* — the orchestrator relays it to a gate and resumes the same agent via a follow-up message with the answer, context intact.

## Phase 4 — Monitor & mid-run control

Monitoring is **event-driven, not polled**: background agents notify on completion, and their final report returns to the orchestrator. Between events, stay responsive to the user — this phase is a loop of reacting to whichever arrives first:

**On agent completion**: verify the claim against authority (PR exists? checks green? artifacts written? full review report published?), update the workstream row and Event Log, then launch the next queued workstream into the freed slot. A findings gate or "blocked" report → gate it (Phase 5), then message the decision back to the same agent to continue.

**On user input at any time** — the run absorbs it live:
- *"also do X, Y"* → run Phase 1 on the additions only (overlap-check against running workstreams), append rows, launch or queue.
- *"stop workstream N"* / *"stop everything"* → stop the task(s), record status `dropped` + reason; the worktree/branch survive for later.
- *"tell agent N to …"* → send a message to that agent; log the instruction in the Event Log.
- *"status?"* → answer from the run file + task list; reconcile against `gh pr list` if stale.
- New standing decisions mid-run → record with scope, and send them to running agents they affect.

**Stall rule**: an agent silent well past its engine's expected runtime → check task status/output; either send a nudge with corrective context, or stop it and gate the failure (retry / reassign / drop). Two failed restarts → stop restarting, escalate.

## Phase 5 — Gates

Gate points: after plans land (staged pipelines), when a PR opens, before every merge, on every "blocked" report, and on any destructive or ambiguous call.

The published `prp-review` report is the findings gate. Present its GitHub URL to the user unless a standing decision already dispositions those findings. Resume the same `prp-deliver` workstream with the decision so it can return accepted findings to its implementation context and re-review the resulting PR.

1. Check the Standing Decisions log. Covered within scope → act, record `auto: <action> per SD-<n>` in the Event Log.
2. Not covered → escalate a **digest**, not a dump: what happened (2–3 lines), what needs deciding, the recommendation and its risk. Group simultaneous gates into one message.
3. Record the user's answer as a new Standing Decision with explicit scope, then convey it — message the affected agent(s), or act directly for merge decisions.

Hard rules regardless of standing decisions: never merge to a protected branch without the user having approved that merge path at least once this run; never delete a branch or worktree with unmerged commits.

## Phase 6 — Integrate

When PRs are green and gate-approved:

1. Build the merge queue: dependency edges first, then ascending conflict risk — pairwise overlap of `gh pr diff <n> --name-only`; overlapping pairs merge farthest apart.
2. Merge strictly one at a time. After each merge, bring remaining branches onto the new base — prefer messaging the owning agent ("rebase onto <base>, resolve, re-run validations, push") so its context handles the conflicts; rebase directly only for trivial cases. Re-check `gh pr checks` before the next merge.
3. Conflicts: mechanical → the owning agent resolves and revalidates; semantic (both sides changed the same behavior) → gate it with both diffs summarized.

## Phase 7 — Close out

1. All workstreams merged, dropped, or handed back → set run status `complete` with a final outcomes table.
2. Clean up remaining worktrees/branches only after verifying merges (`references/launching.md` → Cleanup). Keep the run file — it is the record.
3. Summarize: what shipped (PR links), what was dropped and why, standing decisions worth promoting into CLAUDE.md or memory.

## Gotchas

- Worktree-isolated agents each resolve the same project PRP store. Workstream artifacts (plans, reports) are shared there across worktrees without merging anything. The **run file lives in the project's store** and is never committed by a workstream.
- A follow-up message continues an agent **with its context intact** — always prefer that over spawning a fresh agent to "fix" a live workstream; a fresh agent has none of the history.
- Agents and tasks die with the orchestrator session. For work that must survive it (overnight runs, other harnesses), use the detached fallback lane in `references/launching.md` — same protocol, headless CLI, artifacts as truth.
- Hooks are the observability extension point (e.g. notify or log on subagent stop); wire them per-project if the run file + notifications aren't enough — not required for the skill to work.

## Resources

- `references/launching.md` — launch call shapes, the workstream prompt template, steering/stop/status patterns, the detached headless fallback, cleanup. Read before the first launch of a run.
- `templates/orchestration-run.md` — the run-file format. Read before creating the run file; follow it exactly.
