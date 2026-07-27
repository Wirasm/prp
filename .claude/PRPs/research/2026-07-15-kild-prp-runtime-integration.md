---
date: 2026-07-15T17:31:07Z
git_commit: 9aae960
branch: feature/maintainer-team
repository: kild
topic: "Kild architecture and how Kild drives the PRP framework"
tags: [research, codebase, kild, prp, pi, rooms, worktrees, orchestration]
status: complete
last_updated: 2026-07-15
---

# Research: Kild Driving the PRP Framework

**Date**: 2026-07-15T17:31:07Z  
**Kild Commit**: `9aae960`  
**Kild Branch**: `feature/maintainer-team`  
**Kild Repository**: `/Users/rasmus/Projects/mine/kild`  
**PRP Repository**: `/Users/rasmus/Projects/prp-spaces/PRPs-agentic-eng`

## Research Question

Study `HANDOVER.md` and the Kild repository, with the intended hierarchy that PRP is the framework Kild drives.

## Summary

The intended stack has three boundaries. Kild is the execution and control plane: it owns rooms, participants, worktrees, routing, operator controls, persistence, and how work lands. PRP is the framework Kild drives: its skills define the plan, implement, validate, review, issue, debug, commit, and PR procedures. Pi is the agent runtime: it owns models, sessions, authentication, context, tools, and skill loading (`/Users/rasmus/Projects/mine/kild/HANDOVER.md:8-23`; `/Users/rasmus/Projects/mine/kild/CLAUDE.md:25-34`).

This integration is filesystem- and prompt-mediated rather than an application dependency. Kild starts a pi coding-agent SDK session at a Kild-selected checkout; pi discovers the PRP skills through `~/.agents/skills`; Kild's orchestrator tells a worker which PRP skill to execute; that skill supplies the internal process (`/Users/rasmus/Projects/mine/kild/engine/src/worker.ts:42-74`; `/Users/rasmus/Projects/mine/kild/HANDOVER.md:20-23`; `/Users/rasmus/Projects/mine/kild/.pi/agents/orchestrator.md:20-41`; `/Users/rasmus/Projects/mine/kild/.pi/agents/worker.md:13-22`).

## The Stack

### Kild: Driver and Control Plane

- Kild's mission is one human or agent operator directing isolated coding-agent workstreams through the same surface (`/Users/rasmus/Projects/mine/kild/VISION.md:3-22`).
- The engine owns the CLI, daemon, pi session subprocesses, room lifecycle, worktrees, and HTTP/WebSocket protocol (`/Users/rasmus/Projects/mine/kild/CLAUDE.md:15-20`; `/Users/rasmus/Projects/mine/kild/CLAUDE.md:118-175`).
- A Kild room represents one workstream and may place every participant in the same `kild/<name>` worktree (`/Users/rasmus/Projects/mine/kild/.pi/agents/orchestrator.md:14-18`; `/Users/rasmus/Projects/mine/kild/engine/src/kild/room/room-manager.ts:133-159`).
- Kild resolves who runs where and who receives each turn; it does not implement the PRP planning or implementation procedure in engine code (`/Users/rasmus/Projects/mine/kild/engine/src/kild/room/room-manager.ts:182-205`; `/Users/rasmus/Projects/mine/kild/engine/src/kild/room/room-router.ts:18-69`).

### PRP: Framework Kild Drives

- PRP defines its framework as a PRD plus curated codebase intelligence and an agent/runbook, with executable validation and existing-code patterns (`README.md:38-55`).
- Its primary lifecycle is PRD to phase-aware plan to implementation, followed by PR and review; issue and debug paths provide related procedures (`README.md:85-125`; `README.md:168-208`).
- Kild's orchestrator names PRP skills as task engines: `prp-issue`, `prp-plan`, `prp-implement`, `prp-commit`, `prp-pr`, `prp-review`, and `prp-debug` (`/Users/rasmus/Projects/mine/kild/.pi/agents/orchestrator.md:20-37`).
- Kild's worker treats a named PRP skill as the required process, runs its validations, and reports evidence such as commit SHA, validation output, artifact path, or PR number (`/Users/rasmus/Projects/mine/kild/.pi/agents/worker.md:13-22`).
- PRP artifacts are written into the target checkout under `.claude/PRPs/`, giving Kild and its orchestrator concrete plan/report/review state to verify (`README.md:212-225`; `/Users/rasmus/Projects/mine/kild/.pi/agents/orchestrator.md:43-53`).

### Pi: Agent Runtime

- Kild creates pi sessions through `AuthStorage`, `ModelRegistry`, and `createAgentSession`, passing the final checkout as `cwd` (`/Users/rasmus/Projects/mine/kild/engine/src/worker.ts:42-74`).
- Each live session runs in its own child process because the coding-agent SDK keeps process-global state; Kild communicates with workers using JSONL over stdin/stdout (`/Users/rasmus/Projects/mine/kild/engine/src/kild/sessions.ts:49-71`; `/Users/rasmus/Projects/mine/kild/engine/src/worker.ts:10-17`).
- Kild does not implement PRP skill discovery. It uses pi's default resource loading while supplying `cwd`; the handover records PRP discovery through the shared `~/.agents/skills` standard (`/Users/rasmus/Projects/mine/kild/engine/src/worker.ts:68-74`; `/Users/rasmus/Projects/mine/kild/HANDOVER.md:20-23`; `/Users/rasmus/Projects/mine/kild/HANDOVER.md:41-48`).
- The current machine has 11 `~/.agents/skills/prp-*` symlinks targeting this repository's `.agents/skills/` render, matching the handover's recorded setup (`/Users/rasmus/Projects/mine/kild/HANDOVER.md:41-42`; `scripts/sync_plugin.py:15-25`).

## End-to-End Execution Flow

```text
Human or fleet brain
        |
        v
Kild opens one room/workstream and selects a Kild-owned worktree
        |
        v
Kild spawns pi SDK participants in that shared checkout
        |
        v
pi discovers PRP skills from ~/.agents/skills
        |
        v
orchestrator delegates: "use prp-plan/prp-implement/..."
        |
        v
worker executes the PRP framework procedure in the checkout
        |
        v
PRP writes plan/report/review artifacts and code/commits
        |
        v
worker reports evidence -> orchestrator independently verifies -> human gate
```

1. `kild room` requires the engine, resolves the project checkout, defaults to `orchestrator,worker`, and can assign a shared worktree (`/Users/rasmus/Projects/mine/kild/engine/src/cli.ts:182-220`; `/Users/rasmus/Projects/mine/kild/engine/src/cli.ts:251-269`).
2. `RoomManager` creates one session per participant and passes common `cwd`, worktree name, room id, and participant name (`/Users/rasmus/Projects/mine/kild/engine/src/kild/room/room-manager.ts:133-159`).
3. The worker resolves or attaches the Kild worktree before creating the pi session (`/Users/rasmus/Projects/mine/kild/engine/src/worker.ts:30-39`; `/Users/rasmus/Projects/mine/kild/engine/src/kild/worktree.ts:70-105`).
4. Pi loads the worker personality and available skills; the orchestrator's delegation names the appropriate PRP procedure (`/Users/rasmus/Projects/mine/kild/.pi/agents/orchestrator.md:20-41`; `/Users/rasmus/Projects/mine/kild/.pi/agents/worker.md:13-22`).
5. The worker applies the PRP skill inside the shared checkout and reports evidence through `post_message` (`/Users/rasmus/Projects/mine/kild/engine/src/kild/room/post-message-tool.ts:4-39`; `/Users/rasmus/Projects/mine/kild/.pi/agents/worker.md:17-22`).
6. The orchestrator verifies Git history, validations, PR state, and promised `.claude/PRPs` artifacts before reporting or advancing (`/Users/rasmus/Projects/mine/kild/.pi/agents/orchestrator.md:43-53`).
7. Plan, merge/push, blocker, destructive, and product-shaping points are human-proxy gates; standing decisions may authorize action, otherwise the orchestrator posts a digest to `@human` (`/Users/rasmus/Projects/mine/kild/.pi/agents/orchestrator.md:55-70`).

## Kild Runtime Architecture

### Engine and CLI

- The `kild` binary points to `engine/src/cli.ts`; package scripts expose server, watched development, CLI, tests, typecheck, lint, compiled sidecar, and Flue commands (`/Users/rasmus/Projects/mine/kild/engine/package.json:7-19`).
- The CLI dispatches project, agent, worktree, one-shot run, and room commands (`/Users/rasmus/Projects/mine/kild/engine/src/cli.ts:25-65`).
- A one-shot run uses the live engine when healthy and otherwise creates a pi SDK session in the CLI process (`/Users/rasmus/Projects/mine/kild/engine/src/cli.ts:172-180`; `/Users/rasmus/Projects/mine/kild/engine/src/cli.ts:294-431`).
- The server exposes project, agent, worktree, open-path, session, live-room, and archived-room REST endpoints plus the room WebSocket protocol (`/Users/rasmus/Projects/mine/kild/engine/src/server.ts:53-177`; `/Users/rasmus/Projects/mine/kild/engine/src/server.ts:183-260`).

### Rooms and Addressing

- The room domain separates types, in-memory/persistent registry, routing, and lifecycle management (`/Users/rasmus/Projects/mine/kild/engine/src/kild/room/room-types.ts:3-7`).
- Shared logs write through to `$KILD_HOME/rooms/<id>.json`; restart recovery produces read-only transcripts, not resumable participants (`/Users/rasmus/Projects/mine/kild/engine/src/kild/room/room-registry.ts:13-29`; `/Users/rasmus/Projects/mine/kild/engine/src/kild/room/room-registry.ts:71-75`; `/Users/rasmus/Projects/mine/kild/engine/src/kild/room/room-registry.ts:126-141`).
- Addressing is resolved once in the manager: system notice means no recipient, explicit `to` wins, otherwise mentions are parsed from text (`/Users/rasmus/Projects/mine/kild/engine/src/kild/room/room-manager.ts:182-205`).
- The router broadcasts every post to operator clients and uses authoritative `message.to` only for agent delivery; it filters human/self, preserves one-participant bare-post behavior, and never delivers system notices or implicit narration as turns (`/Users/rasmus/Projects/mine/kild/engine/src/kild/room/room-router.ts:18-69`).
- Room workers receive two agent-held room tools: `post_message` and `invite_agent` (`/Users/rasmus/Projects/mine/kild/engine/src/worker.ts:57-67`).

### Worktree Isolation

- Kild maps a worktree name to branch `kild/<name>` and a deterministic directory beneath `$KILD_HOME/worktrees` (`/Users/rasmus/Projects/mine/kild/engine/src/kild/worktree.ts:17-54`).
- Session worktrees use create-or-attach semantics and never reset an existing shared tree (`/Users/rasmus/Projects/mine/kild/engine/src/kild/worktree.ts:70-105`).
- Automatic pruning removes only clean merged `kild/*` worktrees, preserving dirty, unmerged, and live/in-use trees (`/Users/rasmus/Projects/mine/kild/engine/src/kild/worktree.ts:159-209`).
- PRP's separate `prp-worktree` skill uses an in-repository `.worktrees/` convention, while the handover assigns worktree policy to Kild in this execution lane (`.agents/skills/prp-worktree/SKILL.md:24-33`; `/Users/rasmus/Projects/mine/kild/HANDOVER.md:105-108`).

### Cockpit

- The cockpit is a SvelteKit web client in a thin Tauri shell; the engine owns application/runtime logic (`/Users/rasmus/Projects/mine/kild/app/README.md:1-5`; `/Users/rasmus/Projects/mine/kild/app/src-tauri/src/lib.rs:1-27`).
- REST and reconnecting WebSocket access are concentrated in `app/src/lib/api.ts`, including room open/post/add/halt/close operations (`/Users/rasmus/Projects/mine/kild/app/src/lib/api.ts:12-116`; `/Users/rasmus/Projects/mine/kild/app/src/lib/api.ts:121-209`).
- The Svelte page is the client composition root for project/room/worktree state, participant transcript events, room creation, steering, invites, and reconciliation (`/Users/rasmus/Projects/mine/kild/app/src/routes/+page.svelte:31-117`; `/Users/rasmus/Projects/mine/kild/app/src/routes/+page.svelte:254-333`; `/Users/rasmus/Projects/mine/kild/app/src/routes/+page.svelte:369-416`).

### Flue Layer

- Interactive Kild sessions currently use the pi coding-agent SDK directly; repository guidance states that Flue is not on the session hot path (`/Users/rasmus/Projects/mine/kild/CLAUDE.md:41-47`; `/Users/rasmus/Projects/mine/kild/CLAUDE.md:159-165`).
- The separate Flue layer has concrete demo/workflow callers for one-shot execution, auth bridging, observability, a brain agent, and a self-contained worktree sandbox (`/Users/rasmus/Projects/mine/kild/engine/src/kild/run.ts:25-48`; `/Users/rasmus/Projects/mine/kild/engine/src/kild/auth.ts:10-49`; `/Users/rasmus/Projects/mine/kild/engine/src/kild/observability.ts:10-36`; `/Users/rasmus/Projects/mine/kild/engine/src/kild/brain.ts:14-119`; `/Users/rasmus/Projects/mine/kild/engine/src/flue/worktree-sandbox.ts:8-65`).
- The handover's fleet direction places a brain agent above multiple rooms, holding Kild orchestration tools across workstreams (`/Users/rasmus/Projects/mine/kild/HANDOVER.md:110-121`).

## Handover Verification

### Current Uncommitted State

- Kild is on `feature/maintainer-team` at `9aae960` with eight modified tracked files and untracked `HANDOVER.md`; the modified files match the handover's SDK, CLI, room routing, tests, and personality list (`/Users/rasmus/Projects/mine/kild/HANDOVER.md:59-85`).
- The manifest pins `pi-coding-agent` to `0.80.7` and `pi-ai` to `^0.80.7` (`/Users/rasmus/Projects/mine/kild/engine/package.json:21-25`).
- The CLI kickoff now prepends the lead unless the goal already addresses an actual participant, so `@human` alone does not suppress participant delivery (`/Users/rasmus/Projects/mine/kild/engine/src/cli.ts:207-218`).
- The manager is now the sole addressing resolver, and router regressions cover authoritative empty recipients, join notices, and single-participant halt notices (`/Users/rasmus/Projects/mine/kild/engine/src/kild/room/room-manager.ts:182-205`; `/Users/rasmus/Projects/mine/kild/engine/src/kild/room/room-router.test.ts:42-72`).
- The orchestrator and worker personalities now encode PRP delegation, evidence reporting, independent verification, standing decisions, and gate escalation (`/Users/rasmus/Projects/mine/kild/.pi/agents/orchestrator.md:20-77`; `/Users/rasmus/Projects/mine/kild/.pi/agents/worker.md:13-29`).

### Known Gaps as Implemented

- Operator-side room teardown already exists through WebSocket, CLI, and cockpit; the gap named `close_room` is the absence of an agent-held close tool, because participants receive only post and invite (`/Users/rasmus/Projects/mine/kild/engine/src/kild/room/room-manager.ts:109-119`; `/Users/rasmus/Projects/mine/kild/engine/src/server.ts:249-253`; `/Users/rasmus/Projects/mine/kild/engine/src/worker.ts:57-67`; `/Users/rasmus/Projects/mine/kild/HANDOVER.md:89-92`).
- A no-recipient multi-participant post is persisted and broadcast to operator clients but drives no participant turn and emits no delivery warning (`/Users/rasmus/Projects/mine/kild/engine/src/kild/room/room-manager.ts:204-205`; `/Users/rasmus/Projects/mine/kild/engine/src/kild/room/room-router.ts:49-69`; `/Users/rasmus/Projects/mine/kild/HANDOVER.md:93-95`).
- Project agent discovery checks `.kild/agents`, `.claude/agents`, and `.pi/agents`; global discovery currently checks only `~/.claude/agents` (`/Users/rasmus/Projects/mine/kild/engine/src/kild/agents.ts:16-25`; `/Users/rasmus/Projects/mine/kild/HANDOVER.md:96-98`).
- Kild's current orchestrator personality ends without a rule excluding the separate PRP `prp-worktree` convention (`/Users/rasmus/Projects/mine/kild/.pi/agents/orchestrator.md:68-77`; `/Users/rasmus/Projects/mine/kild/HANDOVER.md:105-108`).

### Evidence Boundary

- The handover records a live GPT-5.6 Terra dogfood in which PRP plan and implement ran through one Kild room with a human gate and independent verification (`/Users/rasmus/Projects/mine/kild/HANDOVER.md:36-57`).
- Kild code confirms the mechanisms required for that run: room participants, shared worktrees, pi SDK sessions, PRP-aware personalities, and evidence-gated delegation (`/Users/rasmus/Projects/mine/kild/engine/src/kild/room/room-manager.ts:133-159`; `/Users/rasmus/Projects/mine/kild/engine/src/worker.ts:42-74`; `/Users/rasmus/Projects/mine/kild/.pi/agents/orchestrator.md:20-70`).
- The exact live-run cost, duration, generated calculator artifact, transcript, and model behavior are historical assertions in `HANDOVER.md`; those artifacts are not stored in the current Kild repository (`/Users/rasmus/Projects/mine/kild/HANDOVER.md:36-57`; `/Users/rasmus/Projects/mine/kild/HANDOVER.md:63-85`).

## Current and Fleet-Level Orchestration

- The current proven unit is one Kild room per PRP-driven workstream, with an orchestrator and worker sharing one Kild-owned checkout (`/Users/rasmus/Projects/mine/kild/.pi/agents/orchestrator.md:14-18`; `/Users/rasmus/Projects/mine/kild/HANDOVER.md:45-52`).
- Current personalities drive individual PRP skills at explicit stages rather than invoking PRP's autonomous `prp-loop` (`/Users/rasmus/Projects/mine/kild/.pi/agents/orchestrator.md:28-37`; `.agents/skills/prp-loop/SKILL.md:7-25`).
- The fleet layer described in the handover is a higher-level brain agent using Kild's control plane across multiple rooms; PRP's orchestration protocol supplies the decomposition/gating/merge concepts, while Kild supplies the runtime mechanisms (`/Users/rasmus/Projects/mine/kild/HANDOVER.md:115-121`).
- The current Flue brain exposes project, agent, worktree, run, open-room, and post-to-room tools, but not the complete multi-room fleet lifecycle described in the handover (`/Users/rasmus/Projects/mine/kild/engine/src/kild/brain.ts:23-105`; `/Users/rasmus/Projects/mine/kild/HANDOVER.md:115-121`).

## Validation Performed

- `bun run typecheck` in `kild/engine`: passed.
- `bun run lint` in `kild/engine`: passed; 38 files checked.
- `bun test` in `kild/engine`: 48 passed, 0 failed across 10 test files.
- `bun run check` in `kild/app`: 0 errors and 1 warning (`@types/node` type definition unavailable to the checker).
- `git diff --check` in Kild: passed.

## Open Questions

- The exact historical dogfood transcript and generated calculator project are not stored in Kild, so their detailed execution can only be documented from `HANDOVER.md`.
