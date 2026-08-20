# Implementation Task Format

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

- Order tasks by real dependency: remove dead paths first, establish a foundational type or scaffold
  before dependent behavior only when the later tasks all benefit, and preserve a working integration path.
- Combine files that implement one coherent behavior; split work with a distinct contract or validation boundary.
- Keep state and decisions with their owner; do not plan pass-through changes across layers when an
  existing owner or primitive can resolve the value directly.
- Describe the outcome first. A task named “Add workflow capability selection” is more useful than “Update five files.”
- Cite the closest useful precedent, not an arbitrary number of examples.
- Make tests part of the behavior they validate, unless shared test infrastructure genuinely has to land first.
- Use the repository's actual commands. A task-level command should fail when that task's behavior is absent.

## Avoid

- Status markers that no workflow maintains.
- “Mirror exactly” when the precedent contains a known poor convention.
- Generic edge-case checklists unrelated to the feature.
- Defensive machinery or tests for unsupported hypothetical behavior.
- Validation that proves only syntax when behavior changed.
- Optional implementation tasks that allow agreed scope to disappear.
- “Fail and move on.” A blocked task blocks completion until the scope or prerequisite is resolved.
