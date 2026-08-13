# Implementation Task Format

> **Kild lane:** you are running inside a kild room, in a workspace (worktree + branch) the kild engine assigned. The driver owns isolation and publishing — SKIP any step below that creates or switches branches or worktrees, pulls or rebases the base branch, pushes, opens PRs, or moves/archives plan artifacts, and never run `gh pr checkout`. Your job ends at implement → validate → commit in the current workspace, reporting evidence. Where a step spawns subagents, do that analysis inline — or ask the room's orchestrator to invite a helper agent.

Write tasks as executable outcomes, not a file inventory. Size each task as the smallest coherent change that can be validated without leaving the system in a knowingly broken intermediate state.

## Required content

```markdown
### N. <Outcome>

**Files and integration points**
- `path/file.ext:line` — CREATE / UPDATE — why this location owns the change

**Implementation**
- Concrete behavior, contract, state transition, or data flow to add or change.
- Existing primitive or pattern to reuse, with `file:line` evidence.
- Important boundary, failure behavior, or compatibility constraint.

**Tests**
- Behavior to prove and the appropriate test surface.

**Validation**
- `<focused command>` — expected observable result.
```

Use only fields that carry information. Add imports, types, schemas, migrations, or gotchas when they are load-bearing; do not repeat details an implementation agent can read directly from the cited file.

## Ordering and sizing

- Order tasks by real dependency and preserve a working integration path.
- Combine files that implement one coherent behavior; split work with a distinct contract or validation boundary.
- Describe the outcome first. A task named “Add workflow capability selection” is more useful than “Update five files.”
- Cite the closest useful precedent, not an arbitrary number of examples.
- Make tests part of the behavior they validate, unless shared test infrastructure genuinely has to land first.
- Use the repository's actual commands. A task-level command should fail when that task's behavior is absent.

## Avoid

- Status markers that no workflow maintains.
- “Mirror exactly” when the precedent contains a known poor convention.
- Generic edge-case checklists unrelated to the feature.
- Validation that proves only syntax when behavior changed.
- Optional implementation tasks that allow agreed scope to disappear.
- “Fail and move on.” A blocked task blocks completion until the scope or prerequisite is resolved.
