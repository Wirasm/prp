# Plan Created — User Report Format

**MANDATORY**: after saving the plan file, display this report to the user in exactly this structure, filling every `{placeholder}` and dropping the `{If ...}` blocks that do not apply.

```markdown
## Plan Created

**File**: `.claude/PRPs/plans/{feature-name}.plan.md`

{If from PRD:}
**Source PRD**: `{prd-file-path}`
**Phase**: #{number} - {phase name}
**PRD Updated**: Status set to `in-progress`, plan linked

{If parallel phases available:}
**Parallel Opportunity**: Phase {X} can run concurrently in a separate worktree.
To start: `git worktree add -b phase-{X} ../project-phase-{X} && cd ../project-phase-{X} && $prp-plan {prd-path}`

**Summary**: {2-3 sentence feature overview}

**Complexity**: {LOW/MEDIUM/HIGH} - {brief rationale}

**Scope**:
- {N} files to CREATE
- {M} files to UPDATE
- {K} total tasks

**Key Patterns Discovered**:
- {Pattern 1 from codebase-explorer/analyst with file:line}
- {Pattern 2 from codebase-explorer/analyst with file:line}

**External Research**:
- {Key doc 1 with version}
- {Key doc 2 with version}

**UX Transformation**:
- BEFORE: {one-line current state}
- AFTER: {one-line new state}

**Risks**:
- {Primary risk}: {mitigation}

**Confidence Score**: {1-10}/10 for one-pass implementation success
- {Rationale for score}

**Next Step**: To execute, run: `$prp-implement .claude/PRPs/plans/{feature-name}.plan.md`
```
