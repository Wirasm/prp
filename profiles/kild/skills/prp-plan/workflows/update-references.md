# Update Plan References

> **Kild lane:** you are running inside a kild room, in a workspace (worktree + branch) the kild engine assigned. The driver owns isolation and publishing — SKIP any step below that creates or switches branches or worktrees, pulls or rebases the base branch, pushes, opens PRs, or moves/archives plan artifacts, and never run `gh pr checkout`. Your job ends at implement → validate → commit in the current workspace, reporting evidence. Where a step spawns subagents, do that analysis inline — or ask the room's orchestrator to invite a helper agent.

Wire a bidirectional relationship between two existing plan files so either artifact leads a reader to the other.

**PLAN**: first plan path

**RELATED**: related plan path

**DIRECTION**: `back` when PLAN depends on RELATED; `forward` when RELATED follows or extends PLAN. Infer when omitted.

## Workflow

1. Resolve both files and stop if either is missing.
2. Infer or verify the direction from the plans' actual relationship.
3. For a current plan, create `## Related Plans` when absent and add the absolute path plus a short label under:
   - `Depends on` for a back reference;
   - `Followed by` for a forward reference.
4. Add the reciprocal relationship to RELATED: a dependency on one side is a follow-up on the other.
5. Do not duplicate an existing link or invent lifecycle status.
6. Report both files and both directions added.

## Legacy plans

Historical plans may contain `## Lifecycle (append-only)` with `Back refs` and `Forward refs`. Preserve that structure when editing one of those plans; do not rewrite the whole artifact merely to add a link. A current plan may therefore link reciprocally with a legacy plan using each plan's native section.

Use expanded absolute store paths so links resolve from every worktree sharing the project store.
