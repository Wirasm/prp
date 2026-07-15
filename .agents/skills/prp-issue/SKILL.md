---
name: prp-issue
description: Investigate a GitHub issue and implement the fix - analyze codebase, create a plan, then code, PR, and self-review. Use when the user wants to investigate or triage a GitHub issue or bug report, fix an investigated issue, implement an issue fix, or invokes $prp-issue.
---

> **Arguments:** `$ARGUMENTS` (and `$1`, `$2`, ...) refer to the arguments given when this skill was invoked. Take them from the user's request; if absent, infer them from the conversation.

# PRP Issue

**Input**: $ARGUMENTS

Two-phase issue workflow: **investigate** an issue into an implementation artifact, then **fix** it from that artifact (code, PR, self-review).

---

## Route on the verb

Read the first token of `$ARGUMENTS` to choose the workflow. Everything after the verb is the issue/artifact argument the workflow operates on.

| First token | Workflow | Operates on |
|-------------|----------|-------------|
| `investigate` | `workflows/investigate.md` | issue number / URL / free-form description |
| `fix` | `workflows/fix.md` | issue number / artifact path (`+ optional --base <branch>`) |
| _no verb_ (a bare issue number, URL, or description) | `workflows/investigate.md` | the whole argument — investigation is the entry point; you investigate before you fix |

**Action**: strip the leading verb (if present), then follow the matching workflow file end-to-end. Do not blend the two — pick one and execute it fully.

---

## Notes

- `investigate` is read-mostly: it analyzes, writes an artifact under `.claude/PRPs/issues/`, commits it, and (for GitHub issues) posts a comment.
- `fix` is **side-effecting**: it creates a branch, commits, opens a PR, and posts a self-review. Only run it once an investigation artifact exists.
- Typical flow: `prp-issue investigate <number>` → review the artifact → `prp-issue fix <number>`.
