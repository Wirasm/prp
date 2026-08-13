# Implementation Report

> **Kild lane:** you are running inside a kild room, in a workspace (worktree + branch) the kild engine assigned. The driver owns isolation and publishing — SKIP any step below that creates or switches branches or worktrees, pulls or rebases the base branch, pushes, opens PRs, or moves/archives plan artifacts, and never run `gh pr checkout`. Your job ends at implement → validate → commit in the current workspace, reporting evidence. Where a step spawns subagents, do that analysis inline — or ask the room's orchestrator to invite a helper agent.

**Plan:** `{absolute plan path}`
**Branch:** `{branch name}`
**Status:** `{COMPLETE | BLOCKED}`

## Outcome

{What now works and why it matters.}

## Validation

| Command or check | Result | Evidence |
| --- | --- | --- |
| `{actual command}` | `{passed | failed}` | {concise factual output} |

## Deviations and Decisions

{Only deviations from the plan and decisions downstream contexts must preserve, or "None."}

## Completion Gate

- **Plan tasks complete:** `{Yes | No}`
- **Acceptance criteria satisfied:** `{Yes | No}`
- **Unresolved blocker:** `{None | exact blocker and evidence}`
- **Recovery:** `{None | why it cannot be completed now and the concrete next action}`

## Intended Commit Scope

{The coherent outcome and changes included in the commit, or what should be committed after a blocker is resolved.}

## Delivery

- **Commit:** `{SHA and message | Not created}`
- **Pull Request:** `{URL | Not opened}`
- **Base / Head:** `{base <- head | Not applicable}`
- **Source PRD:** `{absolute path and phase update | None}`
- **Tracked follow-ups:** `{None | human-visible GitHub issue links for actionable work outside this plan's scope}`
