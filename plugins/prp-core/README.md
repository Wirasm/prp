# PRP Core Plugin

Complete PRP (Product Requirement Prompt) workflow automation for Claude Code, packaged as **Agent Skills**.

## Overview

This plugin provides a comprehensive workflow for creating, executing, and shipping features using the PRP methodology — where **PRP = PRD + curated codebase intelligence + agent/runbook** — designed to enable AI agents to ship production-ready code on the first pass.

Everything ships as **skills** (not slash commands), so each one is both **user-invocable** (type `/prp-core:<name>`) and **agent-invocable** (Claude loads it automatically when your request matches its description). Skills that bundle multiple modes (e.g. `prp-issue`, `prp-review`) keep a lean router in `SKILL.md` and defer detail to `workflows/`.

## Skills

### Planning & spec

| Skill | Description |
|-------|-------------|
| `/prp-core:prp-prd` | Interactive, problem-first PRD generator with an implementation-phases table |
| `/prp-core:prp-plan` | Create an implementation plan (from a PRD or free-form). Also wires bidirectional plan references via its `update-references` workflow |

### Build & ship

| Skill | Description |
|-------|-------------|
| `/prp-core:prp-implement` | Execute a plan with rigorous validation loops; maintains the plan's status markers, lifecycle, and amendments |
| `/prp-core:prp-loop` | **Autonomous** cyclic pipeline: plan → implement → pr → review, looping review→fix until clean. `--until implement` grinds a single plan to green without a PR |
| `/prp-core:prp-orchestrate` | Turn the session into an **orchestrator**: coordinate parallel workstreams running PRP skills in git worktrees, with review gates, a standing-decisions log, and merge sequencing |
| `/prp-core:prp-commit` | Smart commit with natural-language file targeting |
| `/prp-core:prp-pr` | Push the branch and open a PR with template support |

### Review & issues

| Skill | Description |
|-------|-------------|
| `/prp-core:prp-review` | Comprehensive PR review. Single-pass by default; `--agents` fans out specialists (comments, tests, errors, types, code, docs, simplify) |
| `/prp-core:prp-issue` | Two-phase issue workflow: `investigate <issue>` → artifact, then `fix <issue>` → code, PR, self-review |

### Research & debug

| Skill | Description |
|-------|-------------|
| `/prp-core:prp-codebase-question` | Research how the codebase works using parallel agents — documents what exists |
| `/prp-core:prp-debug` | Deep root-cause analysis (5 Whys) — finds the actual cause, not symptoms |
| `/prp-core:prp-research-team` | Design a dynamic research team and plan using agent teams |

### Authoring

| Skill | Description |
|-------|-------------|
| `/prp-core:prp-meta-skill` | Author new skills and refactor fat skills into a lean `SKILL.md` + `references/` (prescribes the craft, not your project's content) |

## Agents

Specialized, advisory agents used by the review and planning skills. They are report-only by design — they analyze and report findings but never modify files or commit (enforced by their prompts, not by a `tools:` allowlist).

### Codebase analysis

| Agent | Description |
|-------|-------------|
| `codebase-analyst` | Documents HOW code works with file:line references |
| `codebase-explorer` | Finds WHERE code lives AND extracts patterns |
| `web-researcher` | Researches the web for docs, APIs, best practices |

### Review

| Agent | Description |
|-------|-------------|
| `code-reviewer` | Project guidelines, bugs, type/module checks |
| `comment-analyzer` | Comment accuracy and maintainability |
| `pr-test-analyzer` | Test coverage quality and gaps |
| `silent-failure-hunter` | Error handling and silent failures |
| `type-design-analyzer` | Type encapsulation and invariants |
| `code-simplifier` | Clarity and maintainability improvements |
| `docs-impact-agent` | Flags stale documentation |

Agents are invoked automatically by `/prp-core:prp-review --agents` and `/prp-core:prp-issue fix`, or manually via the Task tool.

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
    ↓  executes, validates, updates the plan + PRD, archives
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

### Bug fixes: the issue workflow

```
/prp-core:prp-issue investigate 123     # analyze + artifact + post to GitHub
/prp-core:prp-issue fix 123             # implement, PR, self-review
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
│   └── completed/     # archived after implement
├── research/          # codebase research
├── research-plans/    # multi-agent research plans
├── reports/           # implementation reports
├── reviews/           # human-readable PR reviews
├── issues/            # issue investigation artifacts
│   └── completed/
├── debug/             # root-cause analysis reports
├── orchestration/     # parallel-workstream run files
└── state/             # loop state, verdicts, logs, and hook sentinels
```

`<project-key>` is `<slug>-<hash8>`, where the slug comes from the canonical main-checkout basename and `hash8` is the first eight characters of Git's blob hash of that checkout path. This makes every linked worktree resolve to the same store. Set `PRP_HOME` to override the default `~/.prp` root.

If a repository moves, its path-derived key changes. Move the old store to the newly derived key and update `path` in `project.json`; PRP never deletes or auto-adopts the old store.

## PRP methodology

**PRP = PRD + curated codebase intelligence + agent/runbook.** Core principles:

1. **Context is King** — include (or reference) all the context the agent needs
2. **Validation loops** — executable gates the AI runs and fixes until green
3. **Information dense** — real patterns, file:line, commands; no filler
4. **Progressive success** — start small, validate, then enhance

Plans are living artifacts: an append-only Lifecycle header (created/modified/commits/refs), inline task status markers (`[ ] [wip] [x] [f]`), a validation loop, an Amendments log, and a free-form Agent Notes canvas for whatever the template didn't anticipate.

## Troubleshooting

**Plugin not loading** — `/plugin uninstall prp-core@prp-marketplace` then re-install and restart.

**Skills not found** — ensure Claude Code restarted after install; check `/help` and `/plugin`.

## License

MIT — see repository root.

## Support

- Issues: https://github.com/Wirasm/PRPs-agentic-eng/issues
- Docs: https://github.com/Wirasm/PRPs-agentic-eng
