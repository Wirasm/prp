---
name: prp-pr
description: Creates and opens GitHub pull requests. Always use when creating a PR on GitHub, when the user explicitly asks to create or open a PR, when another PRP workflow reaches its PR-creation step, or when the user invokes $prp-pr.
---

> **Arguments:** `$ARGUMENTS` (and `$1`, `$2`, ...) refer to the arguments given when this skill was invoked. Take them from the user's request; if absent, infer them from the conversation.

# Create Pull Request

Create a clear, reviewer-friendly GitHub pull request for the completed work on the current branch.

**Arguments**: $ARGUMENTS

## Scope

Run this at the PR-creation step after the requested work has been done by the current agent, a subagent, or another collaborator. Ensure every change belonging to that work is committed before opening the PR. If intended changes remain uncommitted, invoke `$prp-commit` with a natural-language target that identifies only those changes, then verify the resulting commit. Never sweep unrelated worktree changes into the commit.

The pull request itself is the artifact; do not create a separate local PR document.

## 1. Establish the PR target

Inspect the current branch, repository instructions, remote branches, and Git history. Determine the base in this order:

1. An explicit `--base <branch>`.
2. The base recorded on an existing PR for this branch.
3. The repository's documented development flow.
4. Branch ancestry against likely integration branches such as `development`, `dev`, and the remote default branch.
5. The remote default branch as a fallback.

Use the same resolved base for every log, diff, and PR command. Never assume `main`. If the evidence is genuinely ambiguous, stop and ask rather than opening the PR against a guessed target.

Check whether any open or closed PR already exists for the current branch. If one exists, return its URL and state instead of creating a duplicate.

## 2. Validate the committed work

- Re-read `git status` and the diff after any commit to confirm no intended changes were omitted.
- Confirm the current branch is not the resolved base and contains commits ahead of it.
- Fetch current remote state, then read the complete merge-base diff and commit range against the resolved base—not only the file list or diff stat.
- Compare the diff with the user's requested outcome and repository instructions. Stop if the branch does not contain the intended work or includes unexplained scope.
- Find the repository's pull request template in its supported root, `.github`, or `docs` locations. If several templates could apply and the correct one cannot be inferred, ask which to use.

## 3. Write the pull request

Treat repository rules as syntax constraints, not as the writing-quality standard.

### Title

- Write a concise, human-readable title describing the meaningful outcome.
- Preserve enforced repository syntax such as required types, scopes, or issue identifiers.
- Do not imitate vague or implementation-focused titles merely because they appear in repository history.
- Use Conventional Commit style only when the repository requires or consistently uses it.

**Bad:** `feat(core): add child run traversal and parent event aggregation`

**Good:** `feat(core): workflows can now include a child workflow in the parent run`

### Description

Use the repository's pull request template whenever one exists. Preserve its structure and fill every applicable section with concrete information from the request, diff, commits, and validation evidence.

If no template exists, use this fallback:

```markdown
## Problem

{Explain the original problem and why it matters to the user.}

## Solution

{Briefly explain how the change resolves it, focusing on behavior rather than an inventory of files and functions.}

## Validation

- `{actual command}` — passed
- {Concrete manual verification, when applicable}

{Fixes/Closes/Relates to #N when supported}
```

- Lead with the problem, then the solution. Do not lead with an implementation inventory.
- Report only validation that actually ran. If none ran, say so and explain why; never add generic unchecked boxes as evidence.
- Add `Fixes` or `Closes` only when the PR fully resolves the referenced issue. Use `Relates to` for a non-closing relationship. Do not infer issue linkage from an unexplained bare number.
- Never add AI attribution, a generated-by footer, a robot emoji, or `Co-Authored-By: Claude`.

## 4. Push and create

Push the current branch with upstream tracking when needed. If the remote branch has diverged or the push is rejected, stop and report the conflict; do not rebase or force-push as part of this skill.

Create a ready-for-review PR against the resolved base. Use `--draft` only when the user explicitly requests a draft. Pass the prepared title and body to `gh pr create` without opening an interactive editor.

## 5. Verify and report

Read the created PR back from GitHub and verify its number, URL, title, base, head, draft state, and open state. Check CI status without waiting for pending jobs.

Return the PR URL first, followed by the verified title, `base <- head`, ready/draft state, and current checks. Keep the report concise.

Do not report success until GitHub confirms the PR exists with the intended base and head.
