# Plan Created — User Report

> **Kild lane:** you are running inside a kild room, in a workspace (worktree + branch) the kild engine assigned. The driver owns isolation and publishing — SKIP any step below that creates or switches branches or worktrees, pulls or rebases the base branch, pushes, opens PRs, or moves/archives plan artifacts, and never run `gh pr checkout`. Your job ends at implement → validate → commit in the current workspace, reporting evidence. Where a step spawns subagents, do that analysis inline — or ask the room's orchestrator to invite a helper agent.

Lead with the recommendation, then provide the artifact and only the evidence useful for deciding whether to implement it.

```markdown
## Plan ready

{One or two sentences: recommended approach, invariant, and why this is the simplest supported shape.}

**Plan:** `{expanded absolute plan path}`

{If from a PRD:}
**Source:** `{PRD path}`, phase {number and name} — marked `in-progress` and linked

{If from an issue:}
**Source:** `{issue reference or URL}`
**Published plan:** `{verified issue comment URL}`

{If research or a spike decided the architecture:}
**Decisive evidence:** {source or spike verdict and absolute report path}

{If diagrams were included:}
**Visual review:** {UX flow, architecture, or both}

{If a minor decision remains:}
**Decision to confirm:** {recommendation and consequence}

**Next:** Implement with `the prp-implement skill {expanded absolute plan path}` or its source issue reference.
```

Omit non-applicable lines. Never include a confidence score, file-count inventory, or generic complexity label.
