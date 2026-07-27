---
date: 2026-07-16T14:00:00+03:00
git_commit: b0b6652
branch: development
repository: PRPs-agentic-eng
topic: "Dylan Brain, Kild, and Dylan Record architecture in relation to packaged brain-agent runtimes"
tags: [research, codebase, dylan-brain, kild, dylan-record, agent-runtime]
status: complete
last_updated: 2026-07-16
---

# Research: Dylan Brain Runtime Landscape

**Date**: 2026-07-16T14:00:00+03:00
**Git Commit**: `b0b6652`
**Branch**: `development`
**Repository**: `PRPs-agentic-eng`

## Research Question

Document what currently exists across Dylan Brain, Kild, and Dylan Record, how the three systems interact conceptually, and which parts correspond to capabilities supplied by packaged personal-agent runtimes.

## Repositories Examined

| Repository | Branch | Commit |
|---|---|---|
| Dylan Brain | `development` | `fa42fc93d18f6f0e6b01c4e5c0621eca632dfd23` |
| Kild | `main` | `0ec7ed963cc1bde586499b5ebb0c44c62843f5e7` |
| Dylan Record | `main` | `e8b4fa9142b7c66a218656710cc4c414a6777300` |

## Summary

Dylan Brain is a Claude Code-based personal memory and automation system whose durable state lives in an Obsidian vault. It implements lifecycle hooks, session-context injection, conversation-to-memory routing, periodic reflection, deterministic integrations, and a one-shot proactive heartbeat (`/Users/rasmus/Projects/mine/dylan-brain/CLAUDE.md:12-37`; `/Users/rasmus/Projects/mine/dylan-brain/.claude/settings.json:15-50`).

Kild is a developer cockpit and orchestration engine for multiple coding agents. Its responsibility boundary assigns cognition, models, sessions, tools, and compaction to pi, while Kild owns rooms, workspaces, worktrees, coordination, handoff, and landing (`/Users/rasmus/Projects/mine/kild/VISION.md:24-39`; `/Users/rasmus/Projects/mine/kild/CLAUDE.md:25-34`).

Dylan Record is a focused macOS capture application. It records microphone and system audio, streams audio to Deepgram, writes a live meeting transcript into Obsidian, and optionally adds an Anthropic-generated summary after finalization (`/Users/rasmus/Projects/mine/dylan-record/README.md:3-15`; `/Users/rasmus/Projects/mine/dylan-record/DylanRecord/App/AppState.swift:255-312`).

The three repositories therefore occupy distinct layers: Dylan Record produces personal event data, Dylan Brain stores and interprets personal context and runs personal workflows, and Kild coordinates coding-agent execution. No direct runtime integration between all three is implemented in the examined repositories; their shared integration surface is primarily files, command-line processes, and local HTTP/WebSocket APIs.

## Detailed Findings

### 1. Dylan Brain Product and Storage Model

Dylan Brain describes itself as a local-first “second brain” for email triage and drafting, project and client tracking, Circle monitoring, meeting-context organization, content capture, and an Obsidian-based CRM (`/Users/rasmus/Projects/mine/dylan-brain/.agent/my-second-brain-requirements.md:33-42`).

Persistent memory defaults to `/Users/rasmus/Projects/obsidian-vault/Memory`, with an environment override through `DYLAN_VAULT_PATH`. The storage contract includes `SOUL.md`, `USER.md`, `MEMORY.md`, `BOOTSTRAP.md`, `HEARTBEAT.md`, `HABITS.md`, daily logs, drafts, clients, and projects (`/Users/rasmus/Projects/mine/dylan-brain/.claude/scripts/config.py:22-45`; `/Users/rasmus/Projects/mine/dylan-brain/CLAUDE.md:12-37`).

The repository's root `main.py` only prints a greeting. The live system is entered through Claude Code hooks and standalone Python scripts rather than through a persistent application process (`/Users/rasmus/Projects/mine/dylan-brain/main.py:1-6`; `/Users/rasmus/Projects/mine/dylan-brain/.claude/settings.json:15-50`).

### 2. Dylan Brain Session and Memory Lifecycle

At Claude Code session start, the configured hook reads onboarding instructions, personality, user context, long-term memory, and the current or previous daily log. It caps the assembled material at 20,000 characters and emits it as `SessionStart.additionalContext` (`/Users/rasmus/Projects/mine/dylan-brain/.claude/hooks/session-start-context.py:42-64`; `/Users/rasmus/Projects/mine/dylan-brain/.claude/hooks/session-start-context.py:67-110`; `/Users/rasmus/Projects/mine/dylan-brain/.claude/hooks/session-start-context.py:113-143`).

Pre-compaction and selected session-end events extract recent conversation turns, write temporary context files, and launch a detached memory-flush process (`/Users/rasmus/Projects/mine/dylan-brain/.claude/hooks/pre-compact-flush.py:42-100`; `/Users/rasmus/Projects/mine/dylan-brain/.claude/hooks/session-end-flush.py:63-112`).

The flush process serializes concurrent runs with a file lock, deduplicates recently processed sessions, supplies the current `MEMORY.md` and session context to Claude Agent SDK, and routes retained information into daily logs, client files, project files, working memory, or active drafts (`/Users/rasmus/Projects/mine/dylan-brain/.claude/scripts/memory_flush.py:58-65`; `/Users/rasmus/Projects/mine/dylan-brain/.claude/scripts/memory_flush.py:120-218`; `/Users/rasmus/Projects/mine/dylan-brain/.claude/scripts/memory_flush.py:225-263`).

The reflection process reads preceding daily logs together with `MEMORY.md`, `USER.md`, and `SOUL.md`. Its prompt promotes decisions, lessons, facts, project changes, and upcoming events while limiting working memory to fewer than 50 bullets (`/Users/rasmus/Projects/mine/dylan-brain/.claude/scripts/memory_reflect.py:164-243`).

### 3. Dylan Brain Integrations and Proactivity

Implemented adapters cover Gmail, Calendar, GitHub, Slack, and Circle. Gmail supports message reads, unread counts, sending, trashing, label changes, drafts, newsletter detection, and sent-thread reconciliation (`/Users/rasmus/Projects/mine/dylan-brain/.claude/scripts/integrations/gmail.py:119-236`; `/Users/rasmus/Projects/mine/dylan-brain/.claude/scripts/integrations/gmail.py:244-494`).

The heartbeat script enforces active hours, gathers integration data, loads state, deduplicates alerts, reconciles draft state, and asks an Agent SDK session to produce proactive alerts, drafts, and habit-related actions (`/Users/rasmus/Projects/mine/dylan-brain/.claude/scripts/heartbeat.py:387-445`; `/Users/rasmus/Projects/mine/dylan-brain/.claude/scripts/heartbeat.py:463-546`).

The heartbeat agent receives Read, Write, Edit, Bash, Glob, and Grep tools under `acceptEdits`; Bash calls pass through a command validation hook (`/Users/rasmus/Projects/mine/dylan-brain/.claude/scripts/heartbeat.py:548-569`; `/Users/rasmus/Projects/mine/dylan-brain/.claude/scripts/shared.py:23-67`).

The repository records foundation, lifecycle hooks, integrations, skills, heartbeat, and reflection as complete. Hybrid retrieval, chat interface, security hardening, and deployment remain deferred or pending (`/Users/rasmus/Projects/mine/dylan-brain/CLAUDE.md:182-194`).

Automatic launchd scheduling is represented by a plan that lists wrapper scripts and `setup_scheduler.py` as files to create. Those scheduler files are not part of the current implementation (`/Users/rasmus/Projects/mine/dylan-brain/.claude/PRPs/plans/launchd-scheduling.plan.md:34-41`; `/Users/rasmus/Projects/mine/dylan-brain/.claude/PRPs/reports/phase-6-heartbeat-report.md:92-97`).

### 4. Kild Runtime Boundary

Kild is documented as a single-operator cockpit for directing multiple coding agents across projects. The operator plans, reviews, and steers while coding agents carry out work (`/Users/rasmus/Projects/mine/kild/README.md:10-23`; `/Users/rasmus/Projects/mine/kild/VISION.md:3-22`).

The repository deliberately separates orchestration from cognition. Kild owns workspace placement, rooms, coordination, handoff, and landing; pi owns models, cognition, sessions, tools, compaction, and authentication. The current design is coupled to pi and Flue rather than being provider-neutral (`/Users/rasmus/Projects/mine/kild/VISION.md:24-39`; `/Users/rasmus/Projects/mine/kild/.kild/maintainer/direction.md:21-38`).

The implementation consists of a Bun/TypeScript engine and a Tauri/SvelteKit desktop cockpit. The engine exposes local HTTP and WebSocket interfaces for projects, agents, worktrees, sessions, rooms, room messages, and archived room history (`/Users/rasmus/Projects/mine/kild/README.md:15-23`; `/Users/rasmus/Projects/mine/kild/engine/src/server.ts:31-70`; `/Users/rasmus/Projects/mine/kild/engine/src/server.ts:126-164`; `/Users/rasmus/Projects/mine/kild/engine/src/server.ts:209-423`).

Each live agent session is a worker subprocess communicating with the engine through JSONL. Workers create or attach to worktrees, instantiate pi model and session objects, translate pi events into Kild UI events, and queue prompts sequentially (`/Users/rasmus/Projects/mine/kild/engine/src/kild/sessions.ts:50-125`; `/Users/rasmus/Projects/mine/kild/engine/src/worker.ts:22-52`; `/Users/rasmus/Projects/mine/kild/engine/src/worker.ts:97-169`).

### 5. Kild Fleet Brain

`kild fleet` starts an agent with the `brain` role and enables REST-backed tools for opening rooms, posting to rooms, polling room status, and closing rooms (`/Users/rasmus/Projects/mine/kild/engine/src/cli.ts:185-253`; `/Users/rasmus/Projects/mine/kild/engine/src/worker.ts:66-85`).

The checked-in brain prompt describes the role as a fleet operator proxy. It directs coding work rather than implementing feature code itself, decomposes work into one room and worktree per workstream, keeps a Markdown fleet ledger, verifies evidence, and sequences landing (`/Users/rasmus/Projects/mine/kild/.pi/agents/brain.md:1-21`; `/Users/rasmus/Projects/mine/kild/.pi/agents/brain.md:23-57`; `/Users/rasmus/Projects/mine/kild/.pi/agents/brain.md:61-80`).

The engine's durable data surfaces include project registration and room transcript snapshots. Live rooms and sessions are held in memory, while the fleet ledger's path and update behavior are instructions in the brain prompt (`/Users/rasmus/Projects/mine/kild/engine/src/kild/projects.ts:12-52`; `/Users/rasmus/Projects/mine/kild/engine/src/kild/room/room-registry.ts:105-142`; `/Users/rasmus/Projects/mine/kild/.pi/agents/brain.md:23-42`).

Kild does not implement Dylan Brain's personal data adapters, Obsidian memory lifecycle, meeting ingestion, or personal proactive heartbeat. Its implemented external surface is oriented around projects, worktrees, coding-agent sessions, and rooms (`/Users/rasmus/Projects/mine/kild/engine/src/server.ts:58-70`; `/Users/rasmus/Projects/mine/kild/engine/src/server.ts:126-293`).

### 6. Dylan Record Capture Contract

Dylan Record is a macOS menu-bar recorder that captures microphone and system audio, transcribes through Deepgram, and continuously writes Markdown to an Obsidian vault (`/Users/rasmus/Projects/mine/dylan-record/README.md:3-15`; `/Users/rasmus/Projects/mine/dylan-record/DylanRecord/App/DylanRecordApp.swift:8-27`).

When recording begins, the application creates a crash-recovery draft and provisional live note. Every finalized Deepgram transcript segment is appended to the JSONL draft and triggers a complete rewrite of the live Markdown note (`/Users/rasmus/Projects/mine/dylan-record/DylanRecord/App/AppState.swift:255-312`).

The live-consumption convention is a note in `Meetings/` with `status: recording`. The exported path is `<vault>/Meetings/<yyyy-MM-dd> <meeting name>.md`, and the body uses normalized `Me` and `Them` speaker labels with timestamps (`/Users/rasmus/Projects/mine/dylan-record/README.md:11-15`; `/Users/rasmus/Projects/mine/dylan-record/DylanRecord/Export/MarkdownExporter.swift:28-87`).

On stop and final save, the application drains audio, closes the Deepgram stream, finalizes a local WAV backup, rewrites the note without live status, removes recovery files after success, and optionally submits the complete transcript to Anthropic for a structured summary, decisions, and action items (`/Users/rasmus/Projects/mine/dylan-record/DylanRecord/App/AppState.swift:430-535`; `/Users/rasmus/Projects/mine/dylan-record/DylanRecord/Export/MeetingSummarizer.swift:6-50`; `/Users/rasmus/Projects/mine/dylan-record/DylanRecord/App/AppState.swift:602-618`).

The primary machine-consumption surface is therefore the filesystem. A separate process can discover active and finalized meeting notes from frontmatter and reread atomic file replacements as finalized speech arrives (`/Users/rasmus/Projects/mine/dylan-record/DylanRecord/Export/MarkdownExporter.swift:35-87`; `/Users/rasmus/Projects/mine/dylan-record/DylanRecord/App/AppState.swift:302-312`).

### 7. Current Cross-System Relationship

Dylan Record and Dylan Brain both target the user's Obsidian vault, but Dylan Record writes meeting notes under `Meetings/`, while Dylan Brain's core memory contract is rooted under `Memory/` (`/Users/rasmus/Projects/mine/dylan-record/DylanRecord/Export/MarkdownExporter.swift:66-87`; `/Users/rasmus/Projects/mine/dylan-brain/.claude/scripts/config.py:22-38`).

Dylan Brain's startup context reads its defined memory files and daily logs. The current startup hook does not scan the general `Meetings/` directory (`/Users/rasmus/Projects/mine/dylan-brain/.claude/hooks/session-start-context.py:67-110`).

Kild exposes local CLI, HTTP, and WebSocket control surfaces that another process can call. No Dylan Brain script in the examined repository calls Kild's fleet CLI or room API, and no Kild component reads Dylan Brain's Obsidian memory contract (`/Users/rasmus/Projects/mine/kild/engine/src/cli.ts:47-62`; `/Users/rasmus/Projects/mine/kild/engine/src/server.ts:58-70`; `/Users/rasmus/Projects/mine/kild/engine/src/server.ts:209-423`).

### 8. Capability Boundaries Corresponding to Packaged Runtimes

Dylan Brain currently implements its own equivalents for:

- identity and user-context files (`/Users/rasmus/Projects/mine/dylan-brain/.claude/scripts/config.py:32-38`);
- session-start memory retrieval (`/Users/rasmus/Projects/mine/dylan-brain/.claude/hooks/session-start-context.py:67-143`);
- session-end and pre-compaction memory extraction (`/Users/rasmus/Projects/mine/dylan-brain/.claude/hooks/pre-compact-flush.py:42-100`; `/Users/rasmus/Projects/mine/dylan-brain/.claude/hooks/session-end-flush.py:63-112`);
- long-term memory promotion and reflection (`/Users/rasmus/Projects/mine/dylan-brain/.claude/scripts/memory_flush.py:150-263`; `/Users/rasmus/Projects/mine/dylan-brain/.claude/scripts/memory_reflect.py:164-243`);
- tool adapters for personal services (`/Users/rasmus/Projects/mine/dylan-brain/.claude/scripts/integrations/registry.py:36-72`);
- proactive background work (`/Users/rasmus/Projects/mine/dylan-brain/.claude/scripts/heartbeat.py:387-628`);
- skill instructions stored as repository files (`/Users/rasmus/Projects/mine/dylan-brain/CLAUDE.md:89-103`).

The examined Dylan Brain implementation does not currently include a persistent multi-channel gateway, automatic scheduler installation, completed hybrid semantic retrieval, completed chat session persistence, or completed security-hardening phase (`/Users/rasmus/Projects/mine/dylan-brain/CLAUDE.md:188-194`; `/Users/rasmus/Projects/mine/dylan-brain/.agent/plans/second-brain-prd.md:244-309`; `/Users/rasmus/Projects/mine/dylan-brain/.agent/plans/second-brain-prd.md:786-813`; `/Users/rasmus/Projects/mine/dylan-brain/.agent/plans/second-brain-prd.md:849-927`).

## Validation and Maturity

Dylan Brain defines strict mypy and Ruff checks and documents CLI dry runs and smoke checks. Its Phase 6 report states that no unit-test files were created for that phase (`/Users/rasmus/Projects/mine/dylan-brain/.claude/scripts/pyproject.toml:17-32`; `/Users/rasmus/Projects/mine/dylan-brain/CLAUDE.md:105-130`; `/Users/rasmus/Projects/mine/dylan-brain/.claude/PRPs/reports/phase-6-heartbeat-report.md:86-88`).

Kild defines engine type checking, tests, and Biome validation, plus Svelte application checks. Tests cover agent discovery, models, event translation, routing, room persistence, fleet status, worktree lifecycle, and sandbox behavior (`/Users/rasmus/Projects/mine/kild/engine/package.json:10-19`; `/Users/rasmus/Projects/mine/kild/app/package.json:6-15`; `/Users/rasmus/Projects/mine/kild/engine/src/kild/room/room-router.test.ts:41-136`; `/Users/rasmus/Projects/mine/kild/engine/src/kild/worktree.git.test.ts:39-97`).

Dylan Record defines seven Swift Testing suites covering transcript behavior, Deepgram models and URLs, buffering, recovery drafts, WAV generation, and Markdown export (`/Users/rasmus/Projects/mine/dylan-record/DylanRecordTests/TranscriptManagerTests.swift:4-97`; `/Users/rasmus/Projects/mine/dylan-record/DylanRecordTests/DeepgramClientTests.swift:4-54`; `/Users/rasmus/Projects/mine/dylan-record/DylanRecordTests/MarkdownExporterTests.swift:5-119`).

## Documented Gaps

- Dylan Brain's planned automatic scheduler, chat interface, hybrid retrieval, security-hardening phase, and deployment phase are not recorded as complete (`/Users/rasmus/Projects/mine/dylan-brain/CLAUDE.md:188-194`).
- Dylan Record writes live meeting notes that are available for filesystem consumption, but Dylan Brain's startup hook does not automatically include the general meeting-note directory (`/Users/rasmus/Projects/mine/dylan-record/README.md:11-15`; `/Users/rasmus/Projects/mine/dylan-brain/.claude/hooks/session-start-context.py:67-110`).
- Kild's fleet brain controls coding rooms through polling and local APIs; its handover records archive-triggered completion notification as not yet implemented (`/Users/rasmus/Projects/mine/kild/HANDOVER.md:117-128`; `/Users/rasmus/Projects/mine/kild/engine/src/kild/fleet/rooms-status-tool.ts:7-23`).
- No direct Dylan Brain-to-Kild adapter or Kild-to-Obsidian personal-memory adapter was found in the examined repositories.
