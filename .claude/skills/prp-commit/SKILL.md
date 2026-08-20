---
name: prp-commit
description: Creates Git commits for completed work. Always use when committing changes, when the user explicitly asks to commit the work, when another PRP workflow reaches its commit step, or when the user invokes /prp-commit.
argument-hint: "[target description]"
---

# Commit Intended Work

Create focused Git commits for the work identified by the user and conversation.

**Target**: $ARGUMENTS

## Scope

Infer the intended work from the request, conversation, and current task, including changes produced by subagents. Blank arguments mean infer the target, never commit everything by default.

Inspect staged, unstaged, and untracked changes. Preserve unrelated work in every state. If intended and unrelated changes cannot be separated safely, stop and ask rather than widening the commit.

Keep each commit focused on one coherent outcome. Split unrelated outcomes, but do not fragment one outcome into mechanical implementation layers.

## Message

Write a concise, human-readable subject that explains the meaningful outcome. Commit subjects often become changelog entries or PR titles, so they must make sense without reading the diff.

Use plain language and the repository's exact terms. Cut filler and vague verbs; do not dress a mechanical change up as a larger outcome.

Respect enforced repository syntax such as required types or scopes. Treat Git history as evidence of valid structure, not as the writing-quality standard. Never add AI attribution, generated-by text, robot emoji, or `Co-Authored-By: Claude`.

**Bad:** `refactor(prp-pr): update skill instructions`

**Good:** `refactor(prp-pr): PR creation now uses one focused workflow`

## Commit and verify

Stage and commit only the intended work. Verify the resulting commit contains every intended change, excludes unrelated changes, and leaves the remaining worktree state untouched. Do not amend or push unless explicitly requested.

Return the commit hash, message, committed scope, and any remaining changes. The commit is the artifact; do not create a separate report.
