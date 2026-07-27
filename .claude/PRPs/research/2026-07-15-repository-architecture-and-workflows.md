---
date: 2026-07-15T17:25:23Z
git_commit: b0b6652
branch: development
repository: PRPs-agentic-eng
topic: "Deeply study and understand this repository"
tags: [research, codebase, prp, skills, plugin, codex, orchestration]
status: complete
last_updated: 2026-07-15
---

# Research: Repository Architecture and Workflows

**Date**: 2026-07-15T17:25:23Z  
**Git Commit**: `b0b6652`  
**Branch**: `development`  
**Repository**: `PRPs-agentic-eng`

## Research Question

Deeply study and understand this repository.

## Summary

This repository is a PRP agentic-engineering framework made primarily of skills, agent prompts, templates, hooks, and small Python orchestration tools rather than an application service (`CLAUDE.md:5-9`). It defines a Product Requirement Prompt as a PRD combined with curated codebase intelligence and an agent/runbook, with precise context, existing patterns, and executable validation added for implementation agents (`README.md:38-55`).

The authored source lives under `.claude/`. A synchronization script projects that source into a Claude Code plugin under `plugins/prp-core/` and into Codex-native skills and TOML agents under `.agents/` and `.codex/` (`CLAUDE.md:26-31`; `scripts/sync_plugin.py:42-61`). The main workflow turns a product idea into a PRD, a phase-aware implementation plan, implemented and validated code, a pull request, and a review; separate paths cover issues, debugging, autonomous execution, multi-worktree orchestration, codebase research, and skill authoring (`README.md:85-125`; `README.md:168-208`).

## Detailed Findings

### Repository Purpose and Distribution

- The repository describes itself as a collection of prompts and assets for AI-assisted development, centered on the PRP methodology (`README.md:1-3`, `README.md:38-44`).
- The marketplace exposes one plugin named `prp-core`, sourced from `./plugins/prp-core` (`.claude-plugin/marketplace.json:1-14`).
- Users can install the plugin, copy selected skills, or clone the repository (`README.md:58-81`).
- The plugin manifest describes the package as PRD, plan, implementation, debug, commit, PR, review, issue, research, autonomous-loop, authoring, and specialist-agent tooling (`plugins/prp-core/.claude-plugin/plugin.json:1-7`).

### Source-of-Truth and Generated Trees

- `.claude/skills/` is the working source for skills; a skill contains a `SKILL.md` decision spine and may include `references/`, `templates/`, workflows, and scripts (`CLAUDE.md:26-30`; `CONTRIBUTING.md:17-31`).
- `.claude/agents/` contains the authored specialist-agent prompts (`CLAUDE.md:31-31`).
- `plugins/prp-core/skills/` and `plugins/prp-core/agents/` are generated Claude plugin distributions, while plugin metadata, hooks, and its README are maintained only in the plugin tree (`scripts/sync_plugin.py:6-13`; `scripts/sync_plugin.py:201-221`).
- `.agents/skills/` and `.codex/agents/` are generated Codex renders (`scripts/sync_plugin.py:15-25`; `scripts/sync_plugin.py:223-245`).
- Codex rendering rewrites Claude subagent syntax, removes the `prp-core:` namespace, converts slash skill references to `$prp-*`, adjusts launcher paths, strips `argument-hint`, and explains `$ARGUMENTS` placeholders (`scripts/sync_plugin.py:84-159`).
- Claude-only `prp-orchestrate`, `prp-meta-skill`, and `prp-research-team` are excluded from Codex rendering, and the personal `gpui-researcher` agent is excluded from distributed agent packs (`scripts/sync_plugin.py:54-61`).
- `scripts/sync_plugin.py --check` constructs expected generated trees and compares them with actual files for missing, stale, or changed entries (`scripts/sync_plugin.py:190-302`). At this commit, that check reports `all targets in sync`.

### Core Artifact Lifecycle

- Generated project artifacts live in `.claude/PRPs/`, organized into PRDs, active/completed plans, reports, active/completed issue investigations, and reviews (`README.md:212-225`).
- `prp-prd` runs a gated discovery and grounding process before writing `.claude/PRPs/prds/{name}.prd.md` (`.claude/skills/prp-prd/SKILL.md:26-68`; `.claude/skills/prp-prd/SKILL.md:214-220`).
- A PRD records the problem, evidence, hypothesis, exclusions, metrics, open questions, users, capabilities, technical approach, and an implementation-phase table with dependencies and parallelism (`.claude/skills/prp-prd/SKILL.md:223-350`).
- `prp-plan` accepts a PRD, another document, free-form text, or conversation context; for PRDs it selects the first pending phase whose dependencies are complete (`.claude/skills/prp-plan/SKILL.md:51-99`).
- Planning runs codebase explorer and analyst research in parallel, performs external documentation research after local exploration, and writes `.claude/PRPs/plans/{feature}.plan.md` (`.claude/skills/prp-plan/SKILL.md:132-183`; `.claude/skills/prp-plan/SKILL.md:239-260`).
- The plan template is a downstream contract containing lifecycle metadata, reciprocal references, mandatory reading, actual patterns, file scope, ordered task blocks, task-state markers, validation levels, agent notes, and amendments (`.claude/skills/prp-plan/templates/plan-template.md:1-4`; `.claude/skills/prp-plan/templates/plan-template.md:39-48`; `.claude/skills/prp-plan/templates/plan-template.md:74-181`; `.claude/skills/prp-plan/templates/plan-template.md:185-320`).
- `prp-implement` loads those plan contracts, prepares the Git branch/worktree, implements ordered tasks, validates after file changes, and persists `[wip]`, `[x]`, or `[f]` markers (`.claude/skills/prp-implement/SKILL.md:70-137`; `.claude/skills/prp-implement/SKILL.md:141-197`).
- Implementation runs the plan's static-analysis, test, build, integration, and edge-case commands, creates an implementation report, updates a source PRD phase, appends lifecycle records, and archives the completed plan (`.claude/skills/prp-implement/SKILL.md:201-289`; `.claude/skills/prp-implement/SKILL.md:291-429`).
- `prp-pr` validates repository state, discovers PR templates, derives content from commits and diffs, pushes the branch, creates the PR, and verifies its state and checks through `gh` (`.claude/skills/prp-pr/SKILL.md:21-82`; `.claude/skills/prp-pr/SKILL.md:86-177`; `.claude/skills/prp-pr/SKILL.md:237-290`).
- `prp-review` supports a single reviewer or specialist fan-out, writes `.claude/PRPs/reviews/pr-{N}-review.md`, and posts the result to GitHub when a PR exists (`.claude/skills/prp-review/SKILL.md:13-24`; `.claude/skills/prp-review/SKILL.md:342-485`; `.claude/skills/prp-review/workflows/agents.md:26-80`).

### Issue and Debug Paths

- `prp-issue` is a lean router: `investigate` loads the investigation workflow, `fix` loads the fix workflow, and a bare issue defaults to investigation (`.claude/skills/prp-issue/SKILL.md:15-31`).
- Investigation parses GitHub or free-form input, runs explorer and analyst agents, writes an issue artifact, commits it, and posts a GitHub comment when applicable (`.claude/skills/prp-issue/workflows/investigate.md:19-48`; `.claude/skills/prp-issue/workflows/investigate.md:108-172`; `.claude/skills/prp-issue/workflows/investigate.md:234-255`; `.claude/skills/prp-issue/workflows/investigate.md:445-520`).
- Fix loads and revalidates the investigation, implements and validates the change, creates a linked PR, invokes advisory review agents, and archives the investigation under `issues/completed/` (`.claude/skills/prp-issue/workflows/fix.md:44-135`; `.claude/skills/prp-issue/workflows/fix.md:199-300`; `.claude/skills/prp-issue/workflows/fix.md:304-540`).
- `prp-debug` classifies the input, ranks hypotheses, applies a 5 Whys evidence chain, validates the root cause, and writes a root-cause report with a fix specification (`.claude/skills/prp-debug/SKILL.md:21-72`; `.claude/skills/prp-debug/SKILL.md:72-194`; `.claude/skills/prp-debug/SKILL.md:194-295`).

### Autonomous Loop Runtime

- `prp-loop` launches `.claude/PRPs/scripts/prp_loop.py`, supports new and resumed runs, and can stop after a selected stage (`.claude/skills/prp-loop/SKILL.md:7-39`).
- The Python state machine runs `plan -> implement -> pr -> review`; blocking reviews transition through bounded `fix -> review` cycles (`.claude/PRPs/scripts/prp_loop.py:5-30`; `.claude/PRPs/scripts/prp_loop.py:402-408`).
- State is saved atomically in `.claude/prp-loop.state.json`, and stage history and halt reasons are persisted for resume (`.claude/PRPs/scripts/prp_loop.py:58-72`; `.claude/PRPs/scripts/prp_loop.py:83-113`).
- Each stage runs in a fresh `claude -p` or `codex exec` process selected by persisted CLI state (`.claude/PRPs/scripts/prp_loop.py:123-174`).
- Implementation and fix stages loop until a configured validation command exits successfully or the agent response ends with `VALIDATION: GREEN` (`.claude/PRPs/scripts/prp_loop.py:234-269`).
- Plan, PR, review, and fix stages enforce artifact/state transitions, including a per-cycle JSON review verdict and a new-commit requirement after fixes (`.claude/PRPs/scripts/prp_loop.py:272-399`).
- CLI defaults, bounds, resume behavior, and `--until` termination are implemented in the main loop (`.claude/PRPs/scripts/prp_loop.py:411-490`).

### Parallel Orchestration and Worktrees

- `prp-orchestrate` maps each workstream to one agent, branch, and PR, records a run under `.claude/PRPs/orchestration/`, holds decision gates, and sequences integration (`.claude/skills/prp-orchestrate/SKILL.md:21-38`; `.claude/skills/prp-orchestrate/SKILL.md:67-89`).
- PR-producing work uses isolated worktrees; read-only work can use plain background agents (`.claude/skills/prp-orchestrate/SKILL.md:40-50`).
- The orchestration run-file contract records workstream states, standing decisions, merge queue, and an append-only event log (`.claude/skills/prp-orchestrate/templates/orchestration-run.md:1-45`).
- `prp-worktree` exposes `create`, `list`, and `remove` operations under `.worktrees/` (`.claude/skills/prp-worktree/SKILL.md:13-27`).
- Its Python CLI locates the main checkout, creates branches/worktrees, reports ahead/behind/dirty/diff/merge status, and refuses unsafe removal or branch deletion unless forced (`.claude/skills/prp-worktree/scripts/worktree.py:53-72`; `.claude/skills/prp-worktree/scripts/worktree.py:96-177`).

### Agents and Research Contracts

- Codebase explorer and analyst agents are report-only cartographers: the explorer locates code and patterns, while the analyst traces implementation and data flow; both prohibit change proposals (`.claude/agents/codebase-explorer.md:8-35`; `.claude/agents/codebase-analyst.md:8-35`).
- Review specialists cover code correctness, tests, silent failures, type design, comments, documentation impact, and simplification (`plugins/prp-core/README.md:51-75`).
- `prp-codebase-question` decomposes a question into research areas, assigns explorer/analyst/web agents, requires `file:line` evidence, and writes a research artifact under `.claude/PRPs/research/` (`.claude/skills/prp-codebase-question/SKILL.md:13-30`; `.claude/skills/prp-codebase-question/SKILL.md:64-150`; `.claude/skills/prp-codebase-question/SKILL.md:192-304`).
- `prp-research-team` writes a research-team plan and a sentinel; the plugin Stop hook validates six required sections and blocks completion at most once (`.claude/skills/prp-research-team/SKILL.md:265-291`; `plugins/prp-core/hooks/prp-research-team-stop.sh:9-39`; `plugins/prp-core/hooks/prp-research-team-stop.sh:41-100`).
- The Stop hook is registered only in the Claude plugin and is deliberately not ported to Codex (`plugins/prp-core/hooks/hooks.json:1-13`; `scripts/sync_plugin.py:27-28`).

### Repository Documentation and Historical Material

- `README.md` is the primary methodology, installation, workflow, artifact, and project-structure guide (`README.md:38-67`; `README.md:85-125`; `README.md:168-225`; `README.md:257-267`).
- `README-for-DUMMIES.md` is a simplified command and workflow guide (`README-for-DUMMIES.md:19-69`; `README-for-DUMMIES.md:73-117`).
- `plugins/prp-core/README.md` documents the packaged plugin surface, agents, hook, installation, requirements, and target-project artifacts (`plugins/prp-core/README.md:5-79`; `plugins/prp-core/README.md:116-183`).
- `claude_md_files/` contains framework-specific project-instruction examples (`CLAUDE.md:32-32`).
- `old-prp-commands/` preserves the retired slash-command generation and associated templates/docs for reference only (`README.md:287-291`; `CLAUDE.md:32-33`).

## Architecture Documentation

```text
Authored source (.claude/)
  skills + agents + prp_loop.py
           |
           | scripts/sync_plugin.py
           v
  +--------------------------+-------------------------+
  |                                                    |
Claude plugin                                      Codex render
plugins/prp-core/                                  .agents/skills/
  skills/ + agents/                                .codex/agents/*.toml
  plugin metadata + hook

Target-project workflow
idea -> PRD -> phase plan -> implementation/report -> PR -> review
                    |                                  |
                    +------ persisted .claude/PRPs/ ---+

Automation layers
prp-loop: one bounded plan/implement/PR/review/fix state machine
prp-orchestrate + prp-worktree: multiple isolated workstreams and merge gates
```

The architecture separates declarative agent behavior from small executable mechanisms. Markdown skills define workflow phases and artifact contracts; specialist prompts supply focused analysis; Python scripts handle synchronization, autonomous stage transitions, and worktree operations (`CONTRIBUTING.md:24-31`; `scripts/sync_plugin.py:190-302`; `.claude/PRPs/scripts/prp_loop.py:272-490`; `.claude/skills/prp-worktree/scripts/worktree.py:96-204`).

## Code References

| File | Lines | Description |
|------|-------|-------------|
| [`README.md`](https://github.com/Wirasm/PRPs-agentic-eng/blob/b0b6652/README.md#L38-L55) | 38-55 | PRP definition and added context/pattern/validation layers |
| [`CLAUDE.md`](https://github.com/Wirasm/PRPs-agentic-eng/blob/b0b6652/CLAUDE.md#L26-L41) | 26-41 | Source layout, generated targets, and validation contract |
| [`scripts/sync_plugin.py`](https://github.com/Wirasm/PRPs-agentic-eng/blob/b0b6652/scripts/sync_plugin.py#L42-L77) | 42-77 | Source/target roots, exclusions, and launcher rewrites |
| [`prp-prd/SKILL.md`](https://github.com/Wirasm/PRPs-agentic-eng/blob/b0b6652/.claude/skills/prp-prd/SKILL.md#L214-L350) | 214-350 | PRD output contract and implementation phases |
| [`prp-plan/SKILL.md`](https://github.com/Wirasm/PRPs-agentic-eng/blob/b0b6652/.claude/skills/prp-plan/SKILL.md#L132-L260) | 132-260 | Research, architecture, and plan generation flow |
| [`plan-template.md`](https://github.com/Wirasm/PRPs-agentic-eng/blob/b0b6652/.claude/skills/prp-plan/templates/plan-template.md#L143-L320) | 143-320 | Task, validation, note, and amendment contracts |
| [`prp-implement/SKILL.md`](https://github.com/Wirasm/PRPs-agentic-eng/blob/b0b6652/.claude/skills/prp-implement/SKILL.md#L141-L429) | 141-429 | Execution, validation, reporting, and archival flow |
| [`prp_loop.py`](https://github.com/Wirasm/PRPs-agentic-eng/blob/b0b6652/.claude/PRPs/scripts/prp_loop.py#L234-L490) | 234-490 | Autonomous validation loops and stage state machine |
| [`prp-orchestrate/SKILL.md`](https://github.com/Wirasm/PRPs-agentic-eng/blob/b0b6652/.claude/skills/prp-orchestrate/SKILL.md#L21-L89) | 21-89 | Parallel workstream orchestration and integration gates |
| [`worktree.py`](https://github.com/Wirasm/PRPs-agentic-eng/blob/b0b6652/.claude/skills/prp-worktree/scripts/worktree.py#L96-L177) | 96-177 | Worktree creation, status, and guarded removal |

## Validation Performed

- `uv run scripts/sync_plugin.py --check` returned `all targets in sync`.
- `python3 -m py_compile scripts/sync_plugin.py .claude/PRPs/scripts/prp_loop.py .claude/skills/prp-worktree/scripts/worktree.py` completed successfully.

## Open Questions

- None for the repository-wide architecture and workflow scope requested.
