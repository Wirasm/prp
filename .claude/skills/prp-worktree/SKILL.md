---
name: prp-worktree
description: Git-native worktree management via a bundled single-file CLI - create, list (with per-worktree git stats), and safely tear down isolated checkouts under .worktrees/ for parallel workstreams. Use when the user or an orchestrating skill wants to "create a worktree", "work on this in a separate worktree", "spin up an isolated checkout", "list my worktrees", "clean up / remove a worktree", or invokes /prp-worktree.
argument-hint: create <name> [--base <branch>] | list [--json] | remove <name> [--force] [--delete-branch]
---

# PRP Worktree

Manage isolated git worktrees for parallel workstreams with one bundled script — deterministic create/teardown with safety rails, instead of improvised `git worktree` incantations.

**Input**: $ARGUMENTS (if absent, infer the subcommand and worktree name from the conversation).

## Run it

All operations are one command (never re-implement them with raw git):

```bash
uv run .claude/skills/prp-worktree/scripts/worktree.py create <name> [--base <branch>]
uv run .claude/skills/prp-worktree/scripts/worktree.py list [--base <branch>] [--json]
uv run .claude/skills/prp-worktree/scripts/worktree.py remove <name> [--force] [--delete-branch]
```

- **create** — worktree at `.worktrees/<name>` on branch `<name>` (new from `--base`, or checked out if the branch already exists). Prints the absolute worktree path as its **final line** — `cd` there to start working.
- **list** — every managed worktree with branch, ahead/behind vs base, dirty file count, diffstat (`files +ins/-dels`), merged-into-base, and last-commit age. `--json` for machine consumption.
- **remove** — refuses if the worktree has uncommitted changes (`--force` discards). The branch is kept by default (with a pushed-to-origin report); `--delete-branch` deletes it only if merged into base (`--force` overrides). Never force without first investigating what would be lost.

## Conventions

- Worktrees live **inside the repo** at `.worktrees/<name>` — within sandbox-writable roots on any agent harness — and are auto-excluded from git via `.git/info/exclude`; they never appear in `git status`.
- Branch name = worktree name (slashes allowed in branch; directory name flattens `/` to `-`).
- Default `--base` is the repo's default branch (origin HEAD), falling back to the current branch.
- The script always operates on the **main checkout**, wherever it is run from — including from inside a worktree.

## Gotchas

- Requires `uv` and `git` on PATH; the script is stdlib-only (PEP 723, Python ≥ 3.10).
- `remove` deletes the checkout, not the work: commits live on the branch and survive; only `--force` on a dirty worktree discards uncommitted changes.
- Orchestrating skills compose this by name ("use the prp-worktree skill to create `<name>`") — one worktree per parallel agent prevents checkout collisions.

## Resources

- `scripts/worktree.py` — the CLI (run it, don't read it); `--help` on any subcommand for exact flags.
