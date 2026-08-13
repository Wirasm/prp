---
name: prp-orchestrate
description: Turn the current session into an SDLC orchestrator that coordinates parallel background agents running PRP skills in isolated worktrees - decompose work into workstreams, launch and steer autonomous deliveries, hold human-only and merge gates as the user's proxy, and sequence merges. Use when the user wants to "spawn N agents in separate worktrees", "run prp-issue on these issues in parallel", "orchestrate these features", "act as my orchestrator", "coordinate agents through the PRP pipeline", "ship these issues in parallel", or invokes /prp-orchestrate.
argument-hint: <goal, or list of issues/features/PRD phases> [--max-parallel N] | --resume
---

# PRP Orchestrate

Coordinate multiple PRP workstreams from one session. The orchestrator is the user's proxy: it decomposes the goal, launches autonomous `prp-issue` workstream owners, steers them mid-flight, resolves human-only blockers, and sequences reviewed PRs through merge gates. Each workstream owner keeps planning, implementation, and correction in one context while delegating independent review; the outer orchestrator owns the batch, dependencies, and merges. The run is **live and dynamic** — the user can add work, stop work, redirect an agent, or ask for status at any moment, and the orchestrator absorbs it without restarting anything. The end artifacts are merged PRs plus a run file at `$PRP_DIR/orchestration/<run-id>.md` recording every workstream, decision, and merge.

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
- **Drive workstreams through the native agent tools** — spawn with the Agent/Task tool (background, worktree isolation), steer and continue with SendMessage, stop with the task-stop tool, and check with the task-list/status tools. Never improvise detached CLI processes. Use `prp-loop` only when the user explicitly asks for it.
- **Trust authoritative signals for "done"**: artifacts under the project's PRP store, agent completion reports, `gh pr view/checks`, git state. An agent saying "done" is a claim; a green PR is a fact.
- **Each delivery carries its burden of proof.** The outer orchestrator owns the workstream portfolio, but each `prp-issue` owner must return the plan, implementation report, live PR, green validation and CI, complete published review, and `READY TO MERGE` verdict. Verify that evidence; never reconstruct a delivery from its summary or finish its internal correction loop here.
- **Required CI defines the terminal gate.** Check with `gh pr checks <n> --required`. Pending or failing required checks block acceptance; optional checks remain useful evidence but do not contradict a delivery's terminal state. If the repository has no required CI, a workstream's "validations green" is a self-report, so run the project's own gate against the branch before marking `pr-open`. Re-run more than once where the suite has known flakes — one green run does not distinguish a fix from a lucky sample.
- **The user is the principal.** Every gate decision is either covered by the Standing Decisions log (act, record it as `auto`) or escalated as a short digest (act on the answer, record it). Never guess on destructive or product-shape decisions.
- **Compose skills by name only.** Agents are told to "use the prp-issue skill on #123" or "use the prp-loop skill for detached execution" — never pointed at another skill's files.
- **Think in invariants and primitives.** Do not let a workstream inherit a proposed implementation as its objective. Preserve the required observable outcome, look for the smallest existing primitive that can satisfy it, and prove an uncertain architectural hinge before allowing substantial new machinery.

## Phase 1 — Intake & decompose

1. Establish the goal and enumerate workstreams: GitHub issues, PRD phases, features, or PRs to review. One workstream = one agent = one branch = one PR.
2. Pick each workstream's engine:
   - Issue, existing plan, PRD, document, or description going to a reviewed PR → `prp-issue`
   - Explicit user request for detached, resumable execution or `prp-loop` → `prp-loop`; never select it merely because work may outlive this session
   - Plan only → `prp-plan`; implementation without review → `prp-implement`
   - Review-only → `prp-review` (worktree — it runs `gh pr checkout`); research-only → `prp-codebase-question` (plain background agent)
   - **Feasibility unknown** — "can this be built here", "what would it cost to allow it" → `prp-spike` (worktree). It ends in a verdict, not a PR; what it gates is whether the downstream workstreams should exist at all, so schedule it *before* the work it informs
3. Map dependencies and conflict risk: predict the files each workstream touches. Disjoint → parallel; overlapping → serialize or merge into one workstream.
4. Size the batch from both conflict risk and agent capacity. A delivery owner needs room for one fresh stage coordinator and at least one leaf specialist. Reserve those two slots beyond the root and active delivery owners: `max-parallel = min(3, capacity - 3)`, with a minimum supported capacity of four. If capacity is unknown, default to one. Raise only when workstreams are disjoint and the nested-agent reserve still fits. More parallel agents = more merge surface and more gates.

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

Launch each workstream as a **background agent** via the Agent/Task tool — see `references/launching.md` for the exact call shape and prompt template (read it before the first launch of a run):

- **Worktree isolation is the default** — every workstream that touches the working tree gets its own checkout. The test is *"does it touch the working tree"*, not *"does it open a PR"*: `prp-review` looks read-only but runs `gh pr checkout`, so it gets a worktree too.
- **PR-producing work** → background agent, worktree-isolated: the agent creates its branch, commits, pushes, opens the PR.
- **Read-only working-tree work** — does not modify the checkout (`prp-codebase-question`, `prp-debug`, `prp-plan`, `prp-prd`) → plain background agents. `prp-debug` may publish to GitHub, so give each issue one owning workstream and do not race multiple debuggers against it.
- Record each agent's ID/name and workstream row in the run file at launch. Respect `--max-parallel`: queue the rest, launch as slots free.

Prompts must be self-sufficient (agents inherit nothing from this conversation) and must end with the escalation rule: *if blocked on a decision only a human can make, stop and report the blocker* — the orchestrator relays it to a gate and resumes the same agent via SendMessage with the answer, context intact.

## Phase 4 — Monitor & mid-run control

Monitoring is **event-driven, not polled**: background agents notify on completion, and their final report returns to the orchestrator. Between events, stay responsive to the user — this phase is a loop of reacting to whichever arrives first:

**On agent completion**: verify the claim against authority (PR exists? required checks green, or local gate recorded when none? artifacts written? full review report published with `READY TO MERGE`?), update the workstream row and Event Log, then launch the next queued workstream into the freed slot. An intermediate review report is progress inside `prp-issue`, not completion. A genuine human-only blocker → gate it (Phase 5), then SendMessage the decision back to the same agent to continue.

**On user input at any time** — the run absorbs it live:
- *"also do X, Y"* → run Phase 1 on the additions only (overlap-check against running workstreams), append rows, launch or queue.
- *"stop workstream N"* / *"stop everything"* → stop the task(s), record status `dropped` + reason; the worktree/branch survive for later.
- *"tell agent N to …"* → SendMessage to that agent; log the instruction in the Event Log.
- *"status?"* → answer from the run file + task list; reconcile against `gh pr list` if stale.
- New standing decisions mid-run → record with scope, and SendMessage them to running agents they affect.

**Stall rule**: an agent silent well past its engine's expected runtime → check task status/output; either SendMessage a nudge with corrective context, or stop it and gate the failure (retry / reassign / drop). Two failed restarts → stop restarting, escalate.

## Phase 5 — Gates

Gate points: after plans land in deliberately staged pipelines, before every merge, on genuine human-only blockers, and on any destructive or ambiguous call. Autonomous `prp-issue` workstreams publish every review for visibility but resolve review findings internally until `READY TO MERGE` and CI is green; do not turn those reports into outer-orchestrator gates.

1. Check the Standing Decisions log. Covered within scope → act, record `auto: <action> per SD-<n>` in the Event Log.
2. Not covered → escalate a **digest**, not a dump: what happened (2–3 lines), what needs deciding, the recommendation and its risk. Group simultaneous gates into one message.
3. Record the user's answer as a new Standing Decision with explicit scope, then convey it — SendMessage to the affected agent(s), or act directly for merge decisions.

Hard rules regardless of standing decisions: never merge to a protected branch without the user having approved that merge path at least once this run; never delete a branch or worktree with unmerged commits.

## Phase 6 — Integrate

When PRs are green and gate-approved:

1. Build the merge queue: dependency edges first, then ascending conflict risk — pairwise overlap of `gh pr diff <n> --name-only`; overlapping pairs merge farthest apart.
2. Merge strictly one at a time. After each merge, verify its GitHub merge commit is reachable from `origin/<base>`, update the run file, then clean that workstream's checkout and exact PR-head branches immediately (`references/launching.md` → Cleanup after each merge). Never force checkout cleanup; preserve and report dirty state or changed branch tips.
3. Bring remaining branches onto the new base — prefer SendMessage to the owning agent ("rebase onto <base>, resolve, re-run validations, push") so its context handles the conflicts; rebase directly only for trivial cases. Re-check `gh pr checks <n> --required` before the next merge, or rerun the local gate when no required checks exist.
4. Conflicts: mechanical → the owning agent resolves and revalidates; semantic (both sides changed the same behavior) → gate it with both diffs summarized.

## Phase 7 — Close out

1. All workstreams merged, dropped, or handed back → set run status `complete` with a final outcomes table.
2. Reconcile any worktrees or branches that could not be cleaned after their merge (`references/launching.md` → Cleanup after each merge). Keep the run file — it is the record.
3. Summarize: what shipped (PR links), what was dropped and why, standing decisions worth promoting into CLAUDE.md or memory.

## Gotchas

- Worktree-isolated agents each resolve the same project PRP store. Workstream artifacts (plans, reports) are shared there across worktrees without merging anything. The **run file lives in the project's store** and is never committed by a workstream.
- SendMessage continues an agent **with its context intact** — always prefer it over spawning a fresh agent to "fix" a live workstream; a fresh agent has none of the history.
- Agents and tasks die with the orchestrator session. Preserve branches, PRs, and PRP artifacts for recovery; never assemble a raw detached CLI launch or switch to `prp-loop` unless the user explicitly requested it.
- Hooks are the observability extension point (e.g. notify or log on subagent stop); wire them per-project if the run file + notifications aren't enough — not required for the skill to work.

## Resources

- `references/launching.md` — agent-tool call shapes, the workstream prompt template, SendMessage/stop/status patterns, harness-aware isolation, and post-merge cleanup. Read before the first launch of a run.
- `templates/orchestration-run.md` — the run-file format. Read before creating the run file; follow it exactly.
