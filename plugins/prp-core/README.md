# PRP Core Plugin

Complete PRP (Product Requirement Prompt) workflow automation for Claude Code, packaged as **Agent Skills**.

## Overview

This plugin provides a comprehensive workflow for creating, executing, and shipping features using the PRP methodology — where **PRP = PRD + curated codebase intelligence + agent/runbook** — designed to enable AI agents to ship production-ready code on the first pass.

Everything here ships as **skills** (not slash commands), so each one is both **user-invocable** (type `/prp-core:<name>`) and **agent-invocable** (Claude loads it automatically when your request matches its description). Manual experiments under the source repository's `.claude/skills/in-process/` are not distributed.

## Skills

### Planning & spec

| Skill | Description |
|-------|-------------|
| `/prp-core:prp-prd` | Interactive, problem-first PRD generator with an implementation-phases table |
| `/prp-core:prp-plan` | Create an implementation plan (from a PRD or free-form). Also wires bidirectional plan references via its `update-references` workflow |

### Build & ship

| Skill | Description |
|-------|-------------|
| `/prp-core:prp-implement` | Execute a plan through validated commit and PR; write the durable implementation report |
| `/prp-core:prp-issue` | Own an issue, PRD, document, plan, or idea in one context through a published `READY TO MERGE` review and green CI |
| `/prp-core:prp-loop` | **Detached** cyclic pipeline: plan → implement → PR → review, looping review→fix until clean. `--until implement` stops after a green implementation and open PR |
| `/prp-core:prp-orchestrate` | Turn the session into an **orchestrator**: coordinate autonomous delivery workstreams in git worktrees, with human-only and merge gates, a standing-decisions log, and merge sequencing |
| `/prp-core:prp-commit` | Smart commit with natural-language file targeting |
| `/prp-core:prp-pr` | Push the branch and open a PR with template support |

### Review

| Skill | Description |
|-------|-------------|
| `/prp-core:prp-review` | Agent-based PR review using the skill's current default reviewer set; named specialist scopes are additive |

### Research & debug

| Skill | Description |
|-------|-------------|
| `/prp-core:prp-codebase-question` | Research how the codebase works using parallel agents — documents what exists |
| `/prp-core:prp-debug` | Diagnose a root cause and publish the evidence to the matching GitHub issue |
| `/prp-core:prp-research-team` | Design a dynamic research team and plan using agent teams |

### Authoring

| Skill | Description |
|-------|-------------|
| `/prp-core:prp-meta-skill` | Author new skills and refactor fat skills into a lean `SKILL.md` + `references/` (prescribes the craft, not your project's content) |
| `/prp-core:prp-technical-writing` | Write and edit developer documentation that is clear, concrete, and verified |

## Agents

Specialized, advisory agents used by the review and planning skills. They are report-only by design — they analyze and report findings but never modify files or commit (enforced by their prompts, not by a `tools:` allowlist).

### Codebase analysis

| Agent | Description |
|-------|-------------|
| `codebase-analyst` | Documents HOW code works with file:line references |
| `codebase-explorer` | Finds WHERE code lives AND extracts patterns |
| `root-cause-analyzer` | Proves the causal chain, smallest fix boundary, and regression check for broken behavior |
| `web-researcher` | Researches the web for docs, APIs, best practices |

### Review

| Agent | Description |
|-------|-------------|
| `code-reviewer` | General correctness, sanity, scope, and repository fit |
| `comment-analyzer` | Materially false prose and concrete maintenance traps |
| `pr-test-analyzer` | Meaningful behavior without regression protection |
| `silent-failure-hunter` | Failure paths that become indistinguishable from success |
| `seam-analyzer` | Missing types and drift across system boundaries |
| `code-simplifier` | Removes avoidable machinery through proven smaller primitives |
| `docs-impact-agent` | False or missing documentation that changes reader behavior |

Review agents are invoked automatically by `/prp-core:prp-review` and the review stage of `/prp-core:prp-issue`, or manually via the Task tool.

## Project sidecars

Two optional documents, if your project has them, are read by the skills that need them. Keep them
anywhere in your repository. Link them from your `AGENTS.md` or `CLAUDE.md` so agents reach them
immediately; otherwise the skills find them by name. Do not put them in the PRP store, which lives
outside the repository and holds generated artifacts: these are yours, and they belong in version
control beside the code they govern. Nothing creates them and nothing fails when they are absent.

| File | Holds | Read by |
|------|-------|---------|
| `direction.md` | Product direction and scope: what this project is for, and what it declines to become | `prp-plan`, `prp-review` |
| `engineering.md` | The standard work is checked against, in an engineering manager's voice: the objective function, the taste, the risk posture, what review is for | `prp-plan`, `prp-implement`, `prp-review` and its review agents |

They exist to keep judgment out of prompts. `AGENTS.md` carries durable, short guidance; product
direction changes and belongs in `direction.md`; the standard work is checked against belongs in
`engineering.md`, which holds what needs judgment and hands anything that becomes machine-checkable
to a lint rule, a type, or a CI check. A change that contradicts stated product
direction is a scope question for the operator, not a defect the author can fix in the diff.

## Hooks

The plugin ships one Stop hook, `hooks/prp-research-team-stop.sh`, which validates `prp-research-team` output. The skill writes its plan path to a sentinel file in `~/.prp/<project-key>/state/prp-research-team.state`; on Stop, the hook checks the plan for the six required sections and, if any are missing, blocks completion once with the list of what's absent. It cleans up the sentinel on success, ignores stale sentinels (older than 2 hours), and never blocks twice in a row. Note: the hook ships only with the plugin — if you copy the skill into `.claude/skills/` directly, this validation does not run.

## Workflows

### Large features: PRD → plan → implement

```
/prp-core:prp-prd "user authentication system"
    ↓  creates a PRD with an Implementation Phases table
/prp-core:prp-plan ~/.prp/<project-key>/prds/user-auth.prd.md
    ↓  auto-selects the next pending phase, creates a plan
/prp-core:prp-implement ~/.prp/<project-key>/plans/user-auth-phase-1.plan.md
    ↓  executes, validates, commits, opens the PR, and links delivery to the PRD
repeat /prp-core:prp-plan for the next phase
```

### Medium features: plan → implement

```
/prp-core:prp-plan "add pagination to the API"
/prp-core:prp-implement ~/.prp/<project-key>/plans/add-pagination.plan.md
```

### Hands-off: the autonomous loop

```
/prp-core:prp-loop "add pagination to the API"
    ↓  plan → implement (loop to green) → PR → review → fix → re-review → clean
```

### Input to a reviewed PR

```
/prp-core:prp-issue 123
    ↓  plan → implement → PR → review → correct → re-review → green CI
```

## Installation

### From GitHub (recommended)

```bash
/plugin marketplace add Wirasm/PRPs-agentic-eng
/plugin install prp-core@prp-marketplace
```

### Local development / testing

```bash
/plugin marketplace add /absolute/path/to/PRPs-agentic-eng
/plugin install prp-core@prp-marketplace
# Restart Claude Code
```

### Team automatic installation

Add to your project's `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "prp-marketplace": {
      "source": {
        "source": "github",
        "repo": "Wirasm/PRPs-agentic-eng"
      }
    }
  },
  "enabledPlugins": {
    "prp-core@prp-marketplace": true
  }
}
```

## Requirements

- Claude Code installed
- Git configured; GitHub CLI (`gh`) for PR/issue operations
- [`uv`](https://docs.astral.sh/uv/) — runs the bundled `prp-loop` orchestrator (`skills/prp-loop/scripts/prp_loop.py`)

## Artifacts

Artifacts and runtime state are written outside the repository to the target project's shared PRP store:

```
~/.prp/<project-key>/
├── project.json       # canonical project path and name
├── prds/              # product requirement documents
├── plans/             # implementation plans
├── research/          # codebase research
├── research-plans/    # multi-agent research plans
├── reports/           # implementation reports
├── reviews/           # human-readable PR reviews
├── debug/             # root-cause analysis reports
├── orchestration/     # parallel-workstream run files
└── state/             # loop state, logs, and hook sentinels
```

`<project-key>` is `<slug>-<hash8>`, where the slug comes from the canonical main-checkout basename and `hash8` is the first eight characters of Git's blob hash of that checkout path. This makes every linked worktree resolve to the same store. Set `PRP_HOME` to override the default `~/.prp` root.

If a repository moves, its path-derived key changes. Move the old store to the newly derived key and update `path` in `project.json`; PRP never deletes or auto-adopts the old store.

## PRP methodology

**PRP = PRD + curated codebase intelligence + agent/runbook.** Core principles:

1. **Context is King** — include (or reference) all the context the agent needs
2. **Validation loops** — executable gates the AI runs and fixes until green
3. **Information dense** — real patterns, file:line, commands; no filler
4. **Progressive success** — start small, validate, then enhance

Plans are durable implementation contracts. Implementation results, validation, deviations, commits, and PR delivery live in the matching report so later contexts can recover the current truth without mutating or archiving the plan.

## Troubleshooting

**Plugin not loading** — `/plugin uninstall prp-core@prp-marketplace` then re-install and restart.

**Skills not found** — ensure Claude Code restarted after install; check `/help` and `/plugin`.

## License

MIT — see repository root.

## Support

- Issues: https://github.com/Wirasm/PRPs-agentic-eng/issues
- Docs: https://github.com/Wirasm/PRPs-agentic-eng
