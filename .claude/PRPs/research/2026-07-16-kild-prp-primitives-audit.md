# Kild x PRP primitives audit

**Date:** 2026-07-16  
**Scope:** `~/Projects/mine/kild` at `417a452` and `PRPs-agentic-eng` at `b0b6652`  
**Question:** Does the Kild-driven PRP stack compose as small, explicit, extensible, and reversible primitives?

## Executive verdict

The stack has the right three-layer thesis but does not yet enforce it:

| Layer | Intended owner | Current reality |
|---|---|---|
| Kild | execution topology, sessions, rooms, isolation, landing | Owns these mechanisms, but also carries a second orchestration process in its agent prompts |
| PRP | planning, implementation, validation, review process | Owns those processes, but several skills also create branches/worktrees, push, open PRs, archive artifacts, and orchestrate agents |
| pi | model session, tools, context, auth | Mostly clean; Kild correctly treats it as the runtime substrate |

The system works today because prompts say which overlapping mechanism not to call. That is not a primitive boundary. A primitive boundary is enforced by types, capabilities, command results, and a single owner of each side effect.

The most important rule for the next phase is:

> Kild owns **where, who, and lifecycle**. PRP owns **how to reason and validate inside the assigned workspace**. pi owns **one cognitive session**.

No lower layer should need prose telling it not to exercise a conflicting ownership primitive.

## Primitive test

A component is a reusable primitive when it has all of these properties:

1. **Single responsibility**: one state transition or one policy decision.
2. **Explicit input and output**: success, rejection, and failure are data.
3. **Single authority**: no second component independently decides the same fact.
4. **Composable capability**: callers receive only the operations their role needs.
5. **Idempotent or uniquely identified**: retrying cannot silently duplicate or replace work.
6. **Observable**: state and completion can be queried or subscribed to authoritatively.
7. **Reversible by default**: destructive behavior requires an explicit stronger command.
8. **Harness-neutral policy**: PRP process does not assume a particular control plane.

## What is already primitive-shaped

These should be preserved and strengthened rather than replaced:

- `RoomMessage.to` is resolved once by the room manager and consumed by the router. The recent removal of duplicate mention parsing is exactly the desired primitive direction.
- `routeRoomMessage` is a small delivery-policy primitive with injected delivery effects.
- `ensureWorktree` has correct attach-or-create behavior and preserves an existing branch and checkout.
- Automatic worktree pruning is conservative: it checks merge state, keeps in-use trees, removes non-force, and deletes branches with `-d`.
- One pi session per subprocess is a clear isolation boundary.
- Agent definitions are data files discovered by precedence rather than hard-coded personalities.
- The fleet tools call the same engine room surface used by operator clients.
- PRP skills have named entry points and durable artifacts, making process discoverable and inspectable.

## Findings

### P0: Explicit worktree removal can discard uncommitted work

`removeWorktree()` always runs `git worktree remove --force`. Both the CLI and server call this operation without a separate destructive verb or dirty-state result.

This violates Kild's own rule that uncommitted work is never discarded and is weaker than PRP's worktree removal, which refuses dirty removal unless the caller explicitly supplies `--force`.

**Evidence**

- Kild: `engine/src/kild/worktree.ts:132-134`
- Kild CLI caller: `engine/src/cli.ts:141-153`
- Kild server caller: `engine/src/server.ts:137-153`
- PRP safety contract: `.claude/skills/prp-worktree/SKILL.md:23-25`

**Primitive correction**

Split the operation:

```ts
inspectWorktree(repo, name): Promise<WorktreeState>
removeWorktree(repo, name): Promise<Result<Removed, Dirty | InUse | NotFound>>
forceRemoveWorktree(repo, name, confirmation): Promise<Result<Removed, ...>>
```

The ordinary command must be non-force. Force must be a distinct, explicit capability and should report the files that will be lost before execution.

### P0: Kild and PRP both own the driver lifecycle

Kild's fleet brain and room orchestrator define decomposition, workstreams, ledgers, gates, verification, review, merge order, and cleanup. PRP independently defines the same lifecycle in `prp-orchestrate`, while `prp-loop`, `prp-issue fix`, `prp-implement`, `prp-review`, `prp-pr`, and `prp-worktree` each own additional driver side effects.

Concrete conflicts:

| Kild contract | PRP behavior invoked by current Kild prompts |
|---|---|
| One Kild room/worktree owns isolation | `prp-worktree` creates `.worktrees/<name>` with a separate convention |
| Room work ends committed, with no push/PR | `prp-issue fix` creates a branch, pushes, opens a PR, self-reviews, archives, and pushes again |
| Brain integrates workstreams locally | `prp-orchestrate` expects one agent/branch/PR and agents that push/open PRs |
| Reviewer inspects the shared room checkout and never edits | `prp-review` runs `gh pr checkout`, mutating the current checkout |
| Kild is the orchestration lane | `prp-loop` starts a second headless orchestrator and owns plan through PR review |
| Fleet ledger is `.kild/fleet/` | PRP orchestration ledger is `.claude/PRPs/orchestration/` with a different state model |

The Kild orchestrator currently recommends `prp-issue investigate #N, then fix #N`, directly invoking a workflow that contradicts the fleet brain's "committed, no push/PR" definition of done.

**Evidence**

- Kild ownership thesis: `HANDOVER.md:8-23`
- Kild fleet policy: `.pi/agents/brain.md:23-80`
- Kild room delegation: `.pi/agents/orchestrator.md:28-37`
- PRP orchestration: `.claude/skills/prp-orchestrate/SKILL.md:13-89`
- PRP issue side effects: `.claude/skills/prp-issue/SKILL.md:29-33`, `workflows/fix.md:355-372`, `workflows/fix.md:520-535`
- PRP loop ownership: `.claude/skills/prp-loop/SKILL.md:39-55`
- PRP implement git/lifecycle effects: `.claude/skills/prp-implement/SKILL.md:107-137`, `392-429`
- PRP review checkout: `.claude/skills/prp-review/SKILL.md:79-99`

**Primitive correction**

PRP needs a Kild-compatible process profile built from process primitives:

```text
investigate issue -> artifact
plan -> plan artifact
implement in current workspace -> commits optional, no branch/push/PR
validate -> evidence
review current diff/commit -> findings, no checkout
fix findings in current workspace -> evidence
```

Standalone Claude/Codex adapters may compose those primitives with branch, worktree, push, PR, and archive operations. The Kild adapter must not expose those driver capabilities.

### P1: Room lifecycle commands report success when nothing happened

`RoomManager.open`, `postAs`, `addParticipant`, `halt`, and `close` return `void`. Unknown rooms, duplicate participants, reserved names, capacity rejection, duplicate session IDs, and missing sessions commonly become silent no-ops. REST then returns `{ok:true}` because no exception was thrown.

This makes tools lie:

- `post_room` can say "Posted to the room" for a missing room.
- `close_room` can report success for a missing room.
- `invite_agent` reports "Invited" before the engine accepts or rejects it.
- `RoomRegistry.create` overwrites a live room with the same ID without stopping its former sessions.
- Opening with several participants can partially succeed while returning overall success.

**Evidence**

- Room manager void/no-op operations: `engine/src/kild/room/room-manager.ts:58-70`, `101-138`, `208-217`
- Duplicate room replacement: `engine/src/kild/room/room-registry.ts:35-37`
- Session void/no-op operations: `engine/src/kild/sessions.ts:157-218`
- REST unconditional success: `engine/src/server.ts:272-292`
- Optimistic room tools: `engine/src/kild/room/post-message-tool.ts:31-37`, `invite-agent-tool.ts:29-35`

**Primitive correction**

Every command should return a discriminated result and every async worker control action should have a correlation ID:

```ts
type CommandResult<T, C extends string> =
  | { ok: true; value: T }
  | { ok: false; code: C; message: string };

openRoom(spec): Promise<CommandResult<RoomHandle, OpenRoomError>>
postMessage(command): Promise<CommandResult<RoomMessage, PostError>>
addParticipant(command): Promise<CommandResult<Participant, InviteError>>
haltRoom(id): Promise<CommandResult<RoomSummary, RoomError>>
closeRoom(id): Promise<CommandResult<ArchivedRoom | ClosedEmptyRoom, RoomError>>
```

Room open should validate the complete spec before creating state, then either open fully or roll back every spawned participant.

### P1: Named agents silently degrade to the default agent

`resolveAgentInstructions()` returns `null` both for the explicit default and for an unknown or empty named agent. A misspelled or undiscovered `orchestrator`, `worker`, or `reviewer` therefore starts a generic pi session instead of rejecting the room.

This is especially dangerous in a composable system: a missing Lego block must fail to connect, not silently turn into a different block.

**Evidence**

- `engine/src/kild/agents.ts:89-97`
- Worker consumes `null` as no preamble: `engine/src/worker.ts:123`

**Primitive correction**

Use distinct results:

```ts
resolveAgent(name): DefaultAgent | ResolvedAgent | AgentNotFound | InvalidAgent
```

Validate every participant's model, agent, name, and workspace before room creation.

### P1: A halted room is not actually read-only

`halt()` sets `room.stopped`, but `post()`, `addParticipant()`, and participant message handling do not reject stopped rooms. A halted room can still receive log writes and invitations; delayed control lines from dying workers can mutate it.

**Evidence**

- Halt flag: `engine/src/kild/room/room-manager.ts:121-130`
- No stopped check in add/post: `engine/src/kild/room/room-manager.ts:101-106`, `208-230`

**Primitive correction**

Model room state explicitly:

```ts
type RoomState = 'opening' | 'running' | 'halting' | 'halted' | 'closing' | 'closed';
```

Define allowed transitions centrally. Commands against the wrong state return `invalid_state`.

### P1: Fleet status is not authoritative enough for the brain's contract

The brain prompt says `rooms_status` is the truth for liveness. The tool receives live rooms using the archived-room shape, then returns only room ID, name, participants, and the last two posts. It omits stopped state, participant session state, last activity, worktree path/branch, failure state, and closure events.

A participant process can have exited while still appearing in the room participant snapshot. A silent room is therefore ambiguous, not authoritative.

**Evidence**

- Compact status: `engine/src/kild/fleet/rooms-status.ts:3-19`
- Archived shape lacks live state: `engine/src/kild/room/room-types.ts:84-92`
- Brain depends on status for liveness: `.pi/agents/brain.md:61-72`

**Primitive correction**

Introduce a live projection:

```ts
interface RoomStatus {
  id: RoomId;
  state: RoomState;
  workspace: WorkspaceRef;
  participants: ParticipantStatus[];
  lastActivityAt: number;
  lastMessages: RoomMessage[];
}

type ParticipantStatus = 'starting' | 'idle' | 'working' | 'stopped' | 'failed';
```

Add room events/subscriptions so the brain can react to archive, failure, gate, and completion events without polling.

### P1: Sender identity is a free-form string supplied by the caller

The REST API accepts arbitrary `from`; `post_room` exposes an optional sender override to the model. Any local caller can impersonate `human`, `brain`, a participant, or a system-like label. The recent attribution fix improves the default but does not establish authority.

**Evidence**

- Free-form message sender: `engine/src/kild/room/room-types.ts:25-40`
- REST accepts caller attribution: `engine/src/server.ts:220-280`
- Fleet tool exposes override: `engine/src/kild/fleet/post-room-tool.ts:14-23`

**Primitive correction**

Identity must come from the capability, not command data:

```ts
type Actor =
  | { kind: 'human' }
  | { kind: 'agent'; sessionId: SessionId; participant: ParticipantName }
  | { kind: 'fleet'; sessionId: SessionId }
  | { kind: 'system'; component: string };
```

The engine derives display attribution from the authenticated/attached actor. Remove `from` from model-facing schemas.

### P1: Worker capabilities are modes, not composable capabilities

`worker.ts` uses a nested `inRoom ? roomTools : fleetEnabled ? fleetTools : none` conditional. This prevents a role from receiving an intentional union or subset of capabilities and makes each new role another mode branch.

**Evidence**

- `engine/src/worker.ts:27-29`, `66-85`

**Primitive correction**

Build tools from explicit capabilities:

```ts
type Capability =
  | 'room.post'
  | 'room.invite'
  | 'room.close'
  | 'fleet.open'
  | 'fleet.post'
  | 'fleet.status'
  | 'fleet.close';

buildTools(capabilities, transports): ToolDefinition[]
```

Kild assigns capabilities from engine-owned role/session context. Agent prompts describe behavior but do not grant authority.

### P2: REST, WebSocket, and CLI duplicate command contracts

REST provides atomic room open plus kickoff and engine-generated IDs. WebSocket open uses caller-generated IDs and sends open and kickoff as separate frames. The CLI independently computes kickoff addressing. REST and WebSocket also have separate ad hoc validation.

This has already produced one addressing bug and leaves room creation with different atomicity and validation depending on transport.

**Evidence**

- REST room open: `engine/src/server.ts:220-270`
- WebSocket schema/parser: `engine/src/server.ts:299-365`
- CLI open plus separate post/addressing: `engine/src/cli.ts:313-377`

**Primitive correction**

Define transport-neutral command schemas and one application service:

```text
OpenRoom { commandId, actor, spec, kickoff }
PostRoom { commandId, actor, roomId, content, recipients }
CloseRoom { commandId, actor, roomId, reason }
```

REST, WebSocket, CLI, cockpit, and fleet tools should be adapters over the same commands and results.

### P2: Durable fleet state is prose-owned and duplicated

Kild stores `.kild/fleet/*.md`; PRP orchestration stores `.claude/PRPs/orchestration/*.md`. Both prompts define their own status vocabulary and instruct an LLM to perform atomic writes. There is no parser, transition validator, event append primitive, or reconciliation service.

Markdown is a useful human view, but it should not be the only authoritative mutation API.

**Primitive correction**

Create a small structured `FleetRun` domain with append-only events and derive the Markdown view:

```ts
recordRunEvent(runId, event): Result<RunState, TransitionError>
loadRun(runId): Result<RunState, CorruptRun>
reconcileRun(runId, roomStatuses, gitState): Reconciliation
renderRunMarkdown(state): string
```

PRP may define the generic planning/gate concepts. Kild owns the live run instance because it owns rooms, worktrees, and landing.

### P2: Fleet ledger location conflicts with `kild fleet --worktree`

The brain prompt says the ledger lives in the main checkout. The CLI supports running the fleet brain with `--worktree`, and the worker changes its `cwd` into that worktree before the brain writes files. The prompt cannot make a relative `.kild/fleet` write land in the main checkout.

**Primitive correction**

Remove `--worktree` from fleet-brain sessions, or pass an explicit engine-resolved ledger root/tool. The brain itself should not infer checkout topology.

### P2: Persistence is best-effort and non-atomic

Room history uses synchronous direct overwrite and logs write errors without reflecting degraded persistence in room status. A partial write is skipped on next load as corrupt history. This is acceptable for a cache, but the docs and UI should not imply it is durable truth.

**Primitive correction**

Use temp-file plus rename, expose persistence health, and distinguish ephemeral transcript delivery from durable history.

## Target primitive map

### Kild-owned mechanism

| Primitive | Responsibility |
|---|---|
| `WorkspaceRef` | Main checkout or Kild worktree identity |
| `inspect/create/attach/remove workspace` | Reversible isolation lifecycle |
| `AgentDefinition` | Resolve a named role or return not-found |
| `Session` | Spawn, prompt, stop, observe one pi process |
| `Actor` and `Capability` | Engine-derived identity and authority |
| `Room` state machine | Participant membership and lifecycle |
| `RoomMessage` | Immutable addressed communication |
| `RoomCommand` / `RoomResult` | Transport-neutral acknowledged operations |
| `RoomEvent` / subscription | Push-based observable lifecycle |
| `FleetRun` | Live workstream topology, gates, and landing state |
| `LandingPlan` | Ordered integration of verified branches |

### PRP-owned process

| Primitive | Responsibility |
|---|---|
| `research` | Evidence artifact, no topology changes |
| `investigate` | Root-cause/issue artifact, no branch or PR |
| `plan` | Implementation plan artifact |
| `implement-current-workspace` | Execute a plan where assigned |
| `validate` | Commands, results, and evidence |
| `review-current-change` | Findings against a diff/commit without checkout |
| `fix-findings` | Correct blocking findings in the assigned workspace |
| `commit` | Optional explicit local commit operation |
| `publish` | Optional explicit push/PR operation for standalone harnesses |
| `artifact-transition` | Explicit plan/issue lifecycle update |

### pi-owned runtime

| Primitive | Responsibility |
|---|---|
| Model resolution | Select and instantiate model |
| Agent session | Prompt/turn/context lifecycle |
| Tool invocation | Typed cognitive action surface |
| Authentication | Provider credentials |
| Event stream | Model/tool/token events |

## Composition rules

1. **One owner per side effect.** In the Kild lane, only Kild creates/removes worktrees, moves between branches, opens/closes rooms, and sequences landing.
2. **PRP process primitives run in the current assigned workspace.** They never infer that they should create isolation.
3. **Publishing is a capability, not an implicit final phase.** Push and PR creation happen only when the driver grants and invokes them.
4. **Review never changes checkout implicitly.** The driver supplies the diff, commit range, or PR metadata.
5. **Artifact transitions are explicit commands.** Implementing code does not automatically archive a plan unless the caller requested that transition.
6. **Prompts do not enforce authority.** Tools and engine command handlers do.
7. **Every mutation returns evidence.** No fire-and-forget success text.
8. **Safe operations are the default verbs.** Destructive overrides are separate and conspicuous.
9. **Markdown is a view, not an unvalidated state machine.**
10. **Transport adapters contain no policy.** Addressing, validation, identity, and atomicity live below REST/WS/CLI.

## Migration sequence

Each slice is independently testable and revertible.

### Slice 1: Make removal safe

- Change explicit worktree removal to non-force.
- Return `dirty`, `in_use`, `not_found`, or `removed`.
- Add a separate force endpoint/CLI flag with loss preview.
- Add dirty/untracked/in-use tests.

### Slice 2: Introduce command results

- Add result types to session and room managers.
- Make missing rooms and rejected participants visible.
- Reject duplicate room IDs.
- Propagate results through REST first, then WebSocket/tool acknowledgements.

### Slice 3: Validate room specs before mutation

- Resolve all agents/models/workspace inputs before registry creation.
- Reject unknown named agents.
- Make participant spawning transactional or roll back a partial open.

### Slice 4: Enforce room state

- Add explicit room states and transitions.
- Reject post/invite after halt.
- Surface participant process exit/failure in room status.

### Slice 5: Capability and actor model

- Replace mode-based tool selection with capability assembly.
- Remove free-form `from` from model-facing tools.
- Derive actor identity in the engine.

### Slice 6: One room application API

- Define shared command schemas.
- Move addressing and open-plus-kickoff atomicity into the application service.
- Convert REST, WS, CLI, and fleet tools into thin adapters.

### Slice 7: PRP process/driver split

- Extract harness-neutral `investigate`, `implement-current-workspace`, `review-current-change`, and `validate` contracts.
- Keep current standalone skills as adapters that add branch/push/PR/archive behavior.
- Render a Kild profile that excludes `prp-loop`, `prp-worktree`, and driver-owning variants.
- Update Kild orchestrator mappings to invoke only Kild-compatible process skills.

### Slice 8: Structured fleet state and events

- Add room lifecycle events and brain subscription.
- Add a `FleetRun` event log/state reducer.
- Render `.kild/fleet/*.md` from structured state.
- Remove the duplicate PRP orchestration state machine from the Kild lane.

## Acceptance criteria for "Lego blocks"

The architecture is primitive-first when all of these statements are true:

- Removing a worktree without an explicit force capability cannot lose uncommitted files.
- Opening a room is all-or-nothing and returns a typed result.
- Calling any command on a missing or invalid target returns a typed rejection.
- A requested named agent either resolves exactly or room creation fails.
- A halted room cannot mutate except through an explicit resume/close transition.
- The brain can distinguish running, idle, failed, halted, and closed workstreams.
- A model cannot claim another actor's identity by supplying a string.
- Tool availability is the union of granted capabilities, not a hard-coded role mode.
- Every transport produces identical room behavior.
- Kild can run PRP planning, implementation, validation, and review without exposing a second worktree/orchestration/publish owner.
- PRP can still run standalone by composing the same process primitives with its own driver adapter.
- Each migration slice can be reverted without changing unrelated layers or artifact formats.

## Immediate decisions

1. Treat the forced worktree removal as a correctness bug and fix it before broader fleet expansion.
2. Declare Kild the sole driver in the Kild lane in code/package composition, not only in prompts.
3. Stop delegating `prp-issue fix` and PR-checkout review inside Kild rooms until Kild-compatible process variants exist.
4. Make acknowledged command results the next Kild runtime foundation; later fleet behavior depends on truthful mutations and status.

