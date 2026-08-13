# Implementation Plan Template

> **Kild lane:** you are running inside a kild room, in a workspace (worktree + branch) the kild engine assigned. The driver owns isolation and publishing — SKIP any step below that creates or switches branches or worktrees, pulls or rebases the base branch, pushes, opens PRs, or moves/archives plan artifacts, and never run `gh pr checkout`. Your job ends at implement → validate → commit in the current workspace, reporting evidence. Where a step spawns subagents, do that analysis inline — or ask the room's orchestrator to invite a helper agent.

**MANDATORY**: This is the exact document to fill and save as `$PRP_DIR/plans/{kebab-case-feature-name}.plan.md`. Keep every section heading — downstream tooling (prp-implement, prp-loop, update-references) reads this structure. The task entries and code snippets are illustrative examples from one TypeScript project; replace their content entirely with the target project's real files, patterns, and commands.

---

# Feature: {Feature Name}

**Source PRD:** `{absolute path | None}`
**PRD Phase:** `{phase number | None}`

## Summary

{One paragraph: What we're building and high-level approach}

## User Story

As a {user type}
I want to {action}
So that {benefit}

## Problem Statement

{Specific problem this solves - must be testable}

## Solution Statement

{How we're solving it - architecture overview}

## Metadata

| Field            | Value                                             |
| ---------------- | ------------------------------------------------- |
| Type             | NEW_CAPABILITY / ENHANCEMENT / REFACTOR / BUG_FIX |
| Complexity       | LOW / MEDIUM / HIGH                               |
| Systems Affected | {comma-separated list}                            |
| Dependencies     | {external libs/services with versions}            |
| Estimated Tasks  | {count}                                           |

---

## Lifecycle (append-only)

- **Created:** {ISO-8601 — set once, never changed}
- **Modified:** {append-only ISO list — add one entry every time the plan is built or updated}
- **Commits:** {append-only list of commit SHAs that implemented this plan}
- **Agent / Session:** {append-only list of agent(model) + session id, one per work session}
- **Back refs:** {plans/docs this plan builds on or depends on — `relative/path` + short label}
- **Forward refs:** {plans/docs that build on or extend this plan — `relative/path` + short label}

> **Append-only:** `Created` is set once; every other field is a list you only ever add to — never overwrite or remove existing entries. Keep references bidirectional: when you add a back/forward ref here, add the reciprocal ref on the other plan.

---

## UX Design

### Before State

```
{ASCII diagram - current user experience with data flows}
```

### After State

```
{ASCII diagram - new user experience with data flows}
```

### Interaction Changes

| Location | Before | After | User Impact |
|----------|--------|-------|-------------|
| {path/component} | {old behavior} | {new behavior} | {what changes for user} |

---

## Mandatory Reading

**CRITICAL: Implementation agent MUST read these files before starting any task:**

| Priority | File | Lines | Why Read This |
|----------|------|-------|---------------|
| P0 | `path/to/critical.ts` | 10-50 | Pattern to MIRROR exactly |
| P1 | `path/to/types.ts` | 1-30 | Types to IMPORT |
| P2 | `path/to/test.ts` | all | Test pattern to FOLLOW |

**External Documentation:**
| Source | Section | Why Needed |
|--------|---------|------------|
| [Lib Docs v{version}](url#anchor) | {section name} | {specific reason} |

---

## Patterns to Mirror

**NAMING_CONVENTION:**

```typescript
// SOURCE: src/features/example/service.ts:10-15
// COPY THIS PATTERN:
{actual code snippet from codebase}
```

**ERROR_HANDLING:**

```typescript
// SOURCE: src/features/example/errors.ts:5-20
// COPY THIS PATTERN:
{actual code snippet from codebase}
```

**LOGGING_PATTERN:**

```typescript
// SOURCE: src/features/example/service.ts:25-30
// COPY THIS PATTERN:
{actual code snippet from codebase}
```

**REPOSITORY_PATTERN:**

```typescript
// SOURCE: src/features/example/repository.ts:10-40
// COPY THIS PATTERN:
{actual code snippet from codebase}
```

**SERVICE_PATTERN:**

```typescript
// SOURCE: src/features/example/service.ts:40-80
// COPY THIS PATTERN:
{actual code snippet from codebase}
```

**TEST_STRUCTURE:**

```typescript
// SOURCE: src/features/example/tests/service.test.ts:1-25
// COPY THIS PATTERN:
{actual code snippet from codebase}
```

---

## Files to Change

| File                             | Action | Justification                            |
| -------------------------------- | ------ | ---------------------------------------- |
| `src/features/new/models.ts`     | CREATE | Type definitions - re-export from schema |
| `src/features/new/schemas.ts`    | CREATE | Zod validation schemas                   |
| `src/features/new/errors.ts`     | CREATE | Feature-specific errors                  |
| `src/features/new/repository.ts` | CREATE | Database operations                      |
| `src/features/new/service.ts`    | CREATE | Business logic                           |
| `src/features/new/index.ts`      | CREATE | Public API exports                       |
| `src/core/database/schema.ts`    | UPDATE | Add table definition                     |

---

## NOT Building (Scope Limits)

Explicit exclusions to prevent scope creep:

- {Item 1 - explicitly out of scope and why}
- {Item 2 - explicitly out of scope and why}

---

## Step-by-Step Tasks

Execute in order. Each task is atomic and independently verifiable.

**Status markers** — prefix EVERY task header with one; the build agent updates it inline as it works: `[ ]` idle · `[wip]` in progress · `[x]` complete · `[f]` failed. All tasks start `[ ]`. If a task cannot be made to pass, mark it `[f]`, record why in Agent Notes, and move on if the rest of the plan can still proceed.

### `[ ]` Task {N}: {ACTION} `{path/to/file}`

- **ACTION**: {what to do to this file - CREATE / UPDATE / ADD ...}
- **IMPLEMENT**: {the specific content to implement}
- **MIRROR**: `{path/to/analogous/file:lines}` - {existing pattern to copy exactly}
- **IMPORTS**: {exact import statements the new code needs}
- **GOTCHA**: {known issue to avoid, from research findings}
- **VALIDATE**: `{executable command proving the task is done}`

{Repeat one block per task, in dependency order, numbered from 1.}

---

## Testing Strategy

### Unit Tests to Write

| Test File                                | Test Cases                 | Validates      |
| ---------------------------------------- | -------------------------- | -------------- |
| `src/features/new/tests/schemas.test.ts` | valid input, invalid input | Zod schemas    |
| `src/features/new/tests/errors.test.ts`  | error properties           | Error classes  |
| `src/features/new/tests/service.test.ts` | CRUD ops, access control   | Business logic |

### Edge Cases Checklist

- [ ] Empty string inputs
- [ ] Missing required fields
- [ ] Unauthorized access attempts
- [ ] Not found scenarios
- [ ] Duplicate creation attempts
- [ ] {feature-specific edge case}

---

## Validation Commands

**IMPORTANT**: Replace these placeholders with actual commands from the project's package.json/config.

🔁 **Validation loop:** the plan is not complete until every command below passes (exit 0). On any failure, fix the cause and re-run — loop until all pass. If a check is genuinely impossible, mark it `[f]`, note why in Agent Notes, and move on.

### Level 1: STATIC_ANALYSIS

```bash
{runner} run lint && {runner} run type-check
```

**EXPECT**: Exit 0, no errors or warnings

### Level 2: UNIT_TESTS

```bash
{runner} test {path/to/feature/tests}
```

**EXPECT**: All tests pass, coverage >= 80%

### Level 3: FULL_SUITE

```bash
{runner} test && {runner} run build
```

**EXPECT**: All tests pass, build succeeds

### Level 4: DATABASE_VALIDATION (if schema changes)

Use Supabase MCP to verify:

- [ ] Table created with correct columns
- [ ] RLS policies applied
- [ ] Indexes created

### Level 5: BROWSER_VALIDATION (if UI changes)

Use Browser MCP to verify:

- [ ] UI renders correctly
- [ ] User flows work end-to-end
- [ ] Error states display properly

### Level 6: MANUAL_VALIDATION

{Step-by-step manual testing specific to this feature}

---

## Acceptance Criteria

- [ ] All specified functionality implemented per user story
- [ ] Level 1-3 validation commands pass with exit 0
- [ ] Unit tests cover >= 80% of new code
- [ ] Code mirrors existing patterns exactly (naming, structure, logging)
- [ ] No regressions in existing tests
- [ ] UX matches "After State" diagram

---

## Completion Checklist

- [ ] All tasks completed in dependency order
- [ ] Each task validated immediately after completion
- [ ] Level 1: Static analysis (lint + type-check) passes
- [ ] Level 2: Unit tests pass
- [ ] Level 3: Full test suite + build succeeds
- [ ] Level 4: Database validation passes (if applicable)
- [ ] Level 5: Browser validation passes (if applicable)
- [ ] All acceptance criteria met

---

## Risks and Mitigations

| Risk               | Likelihood   | Impact       | Mitigation                              |
| ------------------ | ------------ | ------------ | --------------------------------------- |
| {Risk description} | LOW/MED/HIGH | LOW/MED/HIGH | {Specific prevention/handling strategy} |

---

## Questionables

_Include this section whenever a decision was assumed rather than certain (and whenever the confidence score is below 8). Surface open decisions here instead of silently deciding — one collapsible entry per open question, with the assumption you took so a human can confirm or correct it._

<details>
<summary>{Open question / assumption / risk}</summary>

{The assumption taken and the rationale behind it.}

</details>

---

## Agent Notes

_Open canvas — the planning agent runs free here. There is no fixed shape: capture anything the sections above did not template for — feature-parity matrices, tradeoffs weighed, approaches considered and rejected, new dependencies (added via the project's package manager), open threads, references, future work. Use whatever structure (prose, tables, lists, diagrams) best serves the reader. Prescription ends here — do not restrict yourself._

{Free-form notes.}

---

## Amendments

_Append-only history of changes made **after** this plan was first built (newest at the bottom). The build and update steps add entries here; never edit or remove existing ones._

<details>
<summary>{ISO-8601 timestamp} — {short summary of what changed}</summary>

{What changed and why.}

</details>
