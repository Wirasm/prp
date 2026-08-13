# Review Report Contract

> **Kild lane:** you are running inside a kild room, in a workspace (worktree + branch) the kild engine assigned. The driver owns isolation and publishing — SKIP any step below that creates or switches branches or worktrees, pulls or rebases the base branch, pushes, opens PRs, or moves/archives plan artifacts, and never run `gh pr checkout`. Your job ends at implement → validate → commit in the current workspace, reporting evidence. Where a step spawns subagents, do that analysis inline — or ask the room's orchestrator to invite a helper agent.

Write every review report in this shape. Omit empty finding rows, but keep all headings so humans and
downstream workflows can find the verdict and blocking categories reliably.

```markdown
---
pr: <number>
base: <base branch>
head: <head branch>
reviewed: <ISO timestamp>
verdict: <READY TO MERGE | NEEDS FIXES | REVIEW INCOMPLETE>
scopes: [code, seams, ...]
publication: <verified GitHub comment/review URL | pending>
---

# PR Review: #<number> — <title>

## Outcome

<One concise paragraph explaining what the PR changes and the review result.>

## Validation

| Command | Result | Evidence |
|---|---|---|
| `<actual command>` | PASS / FAIL / NOT RUN | <decisive detail> |

## Critical Issues (<count>)

| Agent | Finding | Evidence | Required change |
|---|---|---|---|
| `<agent>` | <concrete defect and impact> | `path:line` | <smallest valid correction> |

## Important Issues (<count>)

| Agent | Finding | Evidence | Required change |
|---|---|---|---|

## Suggestions (<count>)

| Agent | Suggestion | Evidence | Why consider it |
|---|---|---|---|

## Strengths

- <Specific behavior or implementation choice supported by the review.>

## Verdict

**<READY TO MERGE | NEEDS FIXES | REVIEW INCOMPLETE>**

<What must happen next, or why the PR is ready.>
```

Rules:

- Every Critical or Important finding needs a concrete impact and file:line evidence.
- Attribute findings to the agent that produced them; validation failures use `validation`.
- Keep suggestions genuinely optional. Never disguise a blocker as a suggestion or vice versa.
- Do not add generic praise, boilerplate checklists, confidence scores, or AI attribution.
- Write `publication: pending` before posting. After GitHub verification, replace it in the local report with the stable comment or review URL; downstream automation treats that URL as required delivery evidence.
