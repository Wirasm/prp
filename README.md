# PRP (Product Requirement Prompts)

A collection of prompts for AI-assisted development with Claude Code.

## Video Walkthrough

https://www.youtube.com/watch?v=KVOZ9s1S9Gk&lc=UgzfwxvFjo6pKEyPo1R4AaABAg

### Support This Work

**Found value in these resources?**

**Buy me a coffee:** https://coff.ee/wirasm

I spent a considerable amount of time creating these resources and prompts. If you find value in this project, please consider buying me a coffee to support my work.

---

### Transform Your Team with AI Engineering Workshops

**Ready to move beyond toy demos to production-ready AI systems?**

**Book a workshop:** https://www.rasmuswiding.com/

**What you'll get:**

- Put your team on a path to become AI power users
- Learn the exact PRP methodology used by top engineering teams
- Hands-on training with Claude Code, PRPs, and real codebases
- From beginner to advanced AI engineering workshops for teams and individuals

**Perfect for:** Engineering teams, Product teams, and developers who want AI that actually works in production

Contact me directly at hello@rasmuswiding.com

---

## What is PRP?

**Product Requirement Prompt (PRP)** = PRD + curated codebase intelligence + agent/runbook

The minimum viable packet an AI needs to ship production-ready code on the first pass.

A PRP supplies an AI coding agent with everything it needs to deliver a vertical slice of working software—no more, no less.

### How PRP Differs from Traditional PRD

A traditional PRD clarifies _what_ the product must do and _why_ customers need it, but deliberately avoids _how_ it will be built.

A PRP keeps the goal and justification sections of a PRD yet adds AI-critical layers:

- **Context**: Precise file paths, library versions, code snippet examples
- **Patterns**: Existing codebase conventions to follow
- **Validation**: Executable commands the AI can run to verify its work

---

## Quick Start

### Option 1: Install the plugin (recommended)

```bash
/plugin marketplace add Wirasm/PRPs-agentic-eng
/plugin install prp-core@prp-marketplace
```

Every skill is then available across all your projects as `/prp-core:<name>`, updated centrally.

### Option 2: Copy the skills you want

```bash
# From your project root — copy individual skills (or the whole folder)
cp -r /path/to/PRPs-agentic-eng/.claude/skills/prp-plan .claude/skills/
```

### Option 3: Clone the repository

```bash
git clone https://github.com/Wirasm/PRPs-agentic-eng.git
cd PRPs-agentic-eng
```

---

## Skills

The `.claude/skills/` directory contains the core PRP workflow as Agent Skills — also distributed as the `prp-core` plugin (invoke as `/prp-core:<name>`):

### Core Workflow

| Command          | Description                                              |
| ---------------- | -------------------------------------------------------- |
| `/prp-prd`       | Interactive PRD generator with implementation phases     |
| `/prp-plan`      | Create implementation plan (from PRD or free-form input) |
| `/prp-implement` | Execute a plan with validation loops                     |

### Issue & Debug Workflow

| Command                  | Description                                      |
| ------------------------ | ------------------------------------------------ |
| `/prp-issue`             | Investigate a GitHub issue, then implement the fix (`investigate` / `fix` verbs) |
| `/prp-debug`             | Deep root cause analysis with 5 Whys methodology |

### Git & Review

| Command       | Description                                       |
| ------------- | ------------------------------------------------- |
| `/prp-commit` | Smart commit with natural language file targeting |
| `/prp-pr`     | Create PR with template support                   |
| `/prp-review` | Comprehensive PR code review                      |

### Autonomous Loop

| Command     | Description                                                            |
| ----------- | --------------------------------------------------------------------- |
| `/prp-loop` | Autonomous cyclic pipeline: plan → implement → pr → review (review→fix loops until clean) |
| `/prp-orchestrate` | Coordinate parallel workstreams running PRP skills in git worktrees, with review gates and merge sequencing |

### Research & Authoring

| Command                  | Description                                                              |
| ------------------------ | ------------------------------------------------------------------------ |
| `/prp-codebase-question` | Research how the codebase works using parallel agents                    |
| `/prp-research-team`     | Design a multi-agent research team and executable research plan          |
| `/prp-meta-skill`        | Author new skills, or refactor fat skills into lean SKILL.md + references |

---

## PRP Loop (Autonomous Execution)

`/prp-loop` drives the full pipeline (`plan → implement → pr → review`) headlessly, running one `claude -p` session per stage and looping `review → fix` until the PR review comes back clean. Progress is tracked in the project's PRP store at `~/.prp/<project-key>/state/prp-loop.state.json`.

### How It Works

```
/prp-loop "add user authentication with JWT"
```

1. **plan** — writes `~/.prp/<project-key>/plans/<feature>.plan.md`
2. **implement** — executes the plan, looping until all validations pass, then commits
3. **pr** — pushes the branch and opens the PR
4. **review** — reviews the PR and writes a `{clean, blocking}` verdict
5. **cycle** — if not clean, blocking findings feed back into a fix pass → push → re-review, until clean or `--max-cycles` is reached

### Usage

```bash
# Run the full pipeline from a feature description
/prp-loop "add user authentication with JWT"

# Grind a single plan to green and stop before PR/review (the old Ralph behaviour)
/prp-loop "add user authentication with JWT" --until implement

# Resume a halted or in-progress loop
/prp-loop --resume
```

### Tips

- `--until <stage>` (`plan` | `implement` | `pr` | `review` | `fix`) halts once that stage completes; `--until implement` is the headless replacement for the retired single-session Ralph loop ("grind one plan to green, no PR")
- Defaults: `--max-cycles 3`, `--max-implement-iterations 10`; base branch is auto-detected
- Pass `--validate "<cmd>"` to give the loop an authoritative green check (exit 0 = pass)
- Works best with plans that have clear, testable validation commands
- State is tracked in `~/.prp/<project-key>/state/prp-loop.state.json`; inspect or resume from there

---

## Workflow Overview

### Large Features: PRD → Plan → Implement

```
/prp-prd "user authentication system"
    ↓
Creates PRD with Implementation Phases table
    ↓
/prp-plan ~/.prp/<project-key>/prds/user-auth.prd.md
    ↓
Auto-selects next pending phase, creates plan
    ↓
/prp-implement ~/.prp/<project-key>/plans/user-auth-phase-1.plan.md
    ↓
Executes plan, updates PRD progress, archives plan
    ↓
Repeat /prp-plan for next phase
```

### Medium Features: Direct to Plan

```
/prp-plan "add pagination to the API"
    ↓
Creates implementation plan from description
    ↓
/prp-implement ~/.prp/<project-key>/plans/add-pagination.plan.md
```

### Bug Fixes: Issue Workflow

```
/prp-issue investigate 123
    ↓
Analyzes issue, creates investigation artifact
    ↓
/prp-issue fix 123
    ↓
Implements fix, creates PR
```

---

## Artifacts Structure

Artifacts and runtime state are stored outside the repository in a per-project directory:

```
~/.prp/<project-key>/
├── project.json       # Canonical project path and name
├── prds/              # Product requirement documents
├── plans/             # Implementation plans
│   └── completed/     # Archived completed plans
├── research/          # Codebase research
├── research-plans/    # Multi-agent research plans
├── reports/           # Implementation reports
├── reviews/           # Human-readable PR reviews
├── issues/            # Issue investigation artifacts
│   └── completed/     # Archived completed investigations
├── debug/             # Root-cause analysis reports
├── orchestration/     # Parallel-workstream run files
└── state/             # Loop state, verdicts, logs, and hook sentinels
```

The project key is derived from the canonical main-checkout path, so all linked worktrees share the same store. Set `PRP_HOME` to override the default `~/.prp` root.

---

## PRD Phases

PRDs include an Implementation Phases table for tracking progress:

```markdown
| #   | Phase | Description | Status      | Parallel | Depends | PRP Plan |
| --- | ----- | ----------- | ----------- | -------- | ------- | -------- |
| 1   | Auth  | User login  | complete    | -        | -       | [link]   |
| 2   | API   | Endpoints   | in-progress | -        | 1       | [link]   |
| 3   | UI    | Frontend    | pending     | with 4   | 2       | -        |
| 4   | Tests | Test suite  | pending     | with 3   | 2       | -        |
```

- **Status**: `pending` → `in-progress` → `complete`
- **Parallel**: Phases that can run concurrently (in separate worktrees)
- **Depends**: Phases that must complete first

---

## PRP Best Practices

1. **Context is King**: Include ALL necessary documentation, examples, and caveats
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix
3. **Information Dense**: Use keywords and patterns from the codebase
4. **Bounded Scope**: Each plan should be completable by an AI in one loop

---

## Project Structure

```
your-project/
├── .claude/
│   ├── skills/              # PRP skills (or install the prp-core plugin)
│   └── agents/              # Custom subagents
├── CLAUDE.md                # Project-specific guidelines
└── src/                     # Your source code
```

---

## Parallel Development with Worktrees

When PRD phases can run in parallel:

```bash
# Phase 3 and 4 can run concurrently
git worktree add -b phase-3-ui ../project-phase-3
git worktree add -b phase-4-tests ../project-phase-4

# Run Claude in each
cd ../project-phase-3 && claude
cd ../project-phase-4 && claude
```

---

## Resources

### Legacy Commands, Templates & Docs

The previous slash-command generation is preserved in `old-prp-commands/` for reference only. That includes its PRP templates (`old-prp-commands/PRPs/templates/` — `prp_base.md`, `prp_story_task.md`, `prp_planning.md`) and curated AI documentation (`old-prp-commands/PRPs/ai_docs/`). The current skills carry their templates inline or in their own `templates/` directories.

---

## License

MIT — see [LICENSE](LICENSE).

---

## Support

I spent a considerable amount of time creating these resources and prompts. If you find value in this project, please consider buying me a coffee to support my work.

**Buy me a coffee:** https://coff.ee/wirasm

---

**The goal is one-pass implementation success through comprehensive context.**
