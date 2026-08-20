# PRP Skills for Dummies

## Contents

- [What is PRP?](#what-is-prp)
- [Setup](#setup)
- [The Skills](#the-skills)
- [The Basic Flow](#the-basic-flow)
- [The PRP Loop (Autonomous Mode)](#the-prp-loop-autonomous-mode)
- [The Git Flow](#the-git-flow)
- [Where Stuff Gets Saved](#where-stuff-gets-saved)
- [Quick Examples](#quick-examples)
- [Tips](#tips)
- [The Old Commands](#the-old-commands)
- [That's It](#thats-it)

---

## What is PRP?

**PRP = PRD + codebase intelligence + validation loop**

You give the AI a detailed plan with context and validation commands. The AI implements, tests, and self-corrects until everything passes.

---

## Setup

Get the skills one of two ways (see the main `README.md` for details):

- **Plugin (recommended):** `/plugin marketplace add Wirasm/PRPs-agentic-eng`, then `/plugin install prp-core@prp-marketplace` — every skill is then available everywhere as `/prp-core:<name>`.
- **Copy:** drop the skills you want from `.claude/skills/` into your project's `.claude/skills/`.

---

## The Skills

### Core Workflow

| Command          | What it does                                    |
| ---------------- | ----------------------------------------------- |
| `/prp-prd`       | Create a PRD with implementation phases         |
| `/prp-plan`      | Create an implementation plan                   |
| `/prp-implement` | Execute a plan with validation loops            |
| `/prp-issue`     | Take any work input to a reviewed PR with green CI |
| `/prp-loop`      | Autonomous pipeline: plan → implement → pr → review |
| `/prp-orchestrate` | Run many workstreams in parallel worktrees, you sit at the gates |

`/prp-deliver` is an in-process, manual-only multi-context experiment. It is not distributed or used by the orchestrator.

### Debug Workflow

| Command       | What it does                                      |
| ------------- | ------------------------------------------------ |
| `/prp-debug`  | Deep root cause analysis (5 Whys)                |

### Git & Review

| Command       | What it does                              |
| ------------- | ----------------------------------------- |
| `/prp-commit` | Smart commit with natural language targeting |
| `/prp-pr`     | Create a pull request                     |
| `/prp-review` | Review a pull request                     |

### Research & Authoring

| Command                  | What it does                                  |
| ------------------------ | --------------------------------------------- |
| `/prp-codebase-question` | Answer "how does the codebase do X?"          |
| `/prp-research-team`     | Plan multi-agent research on a question       |
| `/prp-meta-skill`        | Create new skills or slim down fat ones       |
| `/prp-technical-writing` | Write or edit clear, verified developer docs   |

---

## The Basic Flow

### For Big Features

```
/prp-prd "user authentication system"
    ↓
Creates PRD with phases (stored in .claude/PRPs/prds/)
    ↓
/prp-plan .claude/PRPs/prds/user-auth.prd.md
    ↓
Creates implementation plan for next phase
    ↓
/prp-implement .claude/PRPs/plans/user-auth-phase-1.plan.md
    ↓
Executes plan, runs validations, fixes failures
    ↓
Repeat /prp-plan for next phase
```

### For Medium Features

Skip the PRD. Go straight to a plan:

```
/prp-plan "add pagination to the API"
    ↓
/prp-implement .claude/PRPs/plans/add-pagination.plan.md
```

### From an Issue or Idea to a Reviewed PR

```
/prp-issue 123
```

### For Debugging (Errors, Stack Traces)

```
/prp-debug "TypeError: Cannot read property 'x' of undefined"
    ↓
Creates RCA report with root cause and fix specification
```

---

## The PRP Loop (Autonomous Mode)

For fully autonomous execution, use `/prp-loop` instead of running the stages by hand:

```
/prp-loop "add user authentication with JWT"
```

This runs the whole pipeline in a loop:
1. Plans the feature
2. Implements it, running all validations
3. Opens a PR
4. Reviews the PR; if anything is blocking → fixes it → re-reviews
5. Keeps going until the review is clean

Go make coffee. Come back to a clean PR (or a progress log in `.claude/prp-loop.state.json`).

**Just want to grind one plan to green (no PR), the old Ralph way?** Add `--until implement`:

```
/prp-loop "add user authentication with JWT" --until implement
```

**Resume a halted loop with:** `/prp-loop --resume`

---

## The Git Flow

After implementation:

```
/prp-commit                    # Stage and commit with smart message
/prp-pr                        # Create pull request
/prp-review 123                # Review someone else's PR
```

---

## Where Stuff Gets Saved

```
.claude/PRPs/
├── prds/              # PRD documents
├── plans/             # Implementation plans
├── reports/           # Implementation reports
└── reviews/           # PR reviews
```

---

## Quick Examples

### "I have a rough idea"

```bash
/prp-prd "I want users to be able to like posts"
```

This asks you clarifying questions, does research, and creates a structured PRD with phases.

### "I know what I want to build"

```bash
/prp-plan "add a like button to posts with real-time count updates"
```

Creates a detailed implementation plan with tasks and validation commands.

### "Just build it"

```bash
/prp-loop "add a like button to posts with real-time count updates"
```

Autonomous execution until the PR is clean.

### "There's a bug"

```bash
/prp-issue 456
```

### "I'm done, let's commit"

```bash
/prp-commit typescript files except tests
/prp-pr
```

---

## Tips

1. **Context is king** - The more context in your plan, the better the output
2. **Validation matters** - Plans with test commands work better than plans without
3. **Use the loop for big stuff** - Let `/prp-loop` iterate instead of babysitting
4. **Cap the cycles** - Tune `--max-cycles` / `--max-implement-iterations` on `/prp-loop`
5. **Start specific** - "Add OAuth2 with Google" beats "add authentication"

---

## The Old Commands

Previous commands like `/prp-base-create`, `/prp-spec-create`, `/api-contract-define`, etc. are preserved in `old-prp-commands/` for reference. The new streamlined flow replaces all of them.

---

## That's It

1. Big feature? → `/prp-prd` → `/prp-plan` → `/prp-loop`
2. Medium feature? → `/prp-plan` → `/prp-implement`
3. Issue, plan, document, or idea to reviewed PR? → `/prp-issue <input>`
4. Weird bug? → `/prp-debug "error message"`
5. Done? → `/prp-commit` → `/prp-pr`

Happy building.
