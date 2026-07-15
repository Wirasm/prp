# Task Block Format — Field Detail & Worked Examples

How to write the entries in the plan's "Step-by-Step Tasks" section. The section skeleton (status markers + the generic task block) lives in `templates/plan-template.md`; this file holds the field-by-field detail and a full worked example sequence.

## Fields

Each task is a bullet list under a `### `[ ]` Task N: {ACTION} `{file}`` header. Use the fields that apply:

- **ACTION** — what to do to the file (CREATE / UPDATE / ADD ...)
- **IMPLEMENT** — the specific content to implement (functions, columns, schemas)
- **MIRROR** — `file:line` of the existing codebase pattern to copy exactly
- **IMPORTS** — exact import statements the new code needs
- **TYPES** — type definitions or inference patterns to use
- **PATTERN** — the design pattern or structural rule to follow
- **GOTCHA** — known issue to avoid, discovered in Phase 2/3 research
- **VALIDATE** — executable command proving the task is done

Every task MUST have at least MIRROR (or PATTERN) and VALIDATE. GOTCHA entries come from real research findings, not invented warnings.

## Worked example sequence

Illustrative examples from one TypeScript project — replace their content entirely with the target project's real files, patterns, and commands. Note the dependency order: schema → types → validation → errors → repository → service → public API → tests.

### `[ ]` Task 1: UPDATE `src/core/database/schema.ts`

- **ACTION**: ADD table definition to schema
- **IMPLEMENT**: {specific columns, types, constraints}
- **MIRROR**: `src/core/database/schema.ts:XX-YY` - follow existing table pattern
- **IMPORTS**: `import { pgTable, text, timestamp } from "drizzle-orm/pg-core"`
- **GOTCHA**: {known issue to avoid, e.g., "use uuid for id, not serial"}
- **VALIDATE**: `npx tsc --noEmit` - types must compile

### `[ ]` Task 2: CREATE `src/features/new/models.ts`

- **ACTION**: CREATE type definitions file
- **IMPLEMENT**: Re-export table, define inferred types
- **MIRROR**: `src/features/projects/models.ts:1-10`
- **IMPORTS**: `import { things } from "@/core/database/schema"`
- **TYPES**: `type Thing = typeof things.$inferSelect`
- **GOTCHA**: Use `$inferSelect` for read types, `$inferInsert` for write
- **VALIDATE**: `npx tsc --noEmit`

### `[ ]` Task 3: CREATE `src/features/new/schemas.ts`

- **ACTION**: CREATE Zod validation schemas
- **IMPLEMENT**: CreateThingSchema, UpdateThingSchema
- **MIRROR**: `src/features/projects/schemas.ts:1-30`
- **IMPORTS**: `import { z } from "zod/v4"` (note: zod/v4 not zod)
- **GOTCHA**: z.record requires two args in v4
- **VALIDATE**: `npx tsc --noEmit`

### `[ ]` Task 4: CREATE `src/features/new/errors.ts`

- **ACTION**: CREATE feature-specific error classes
- **IMPLEMENT**: ThingNotFoundError, ThingAccessDeniedError
- **MIRROR**: `src/features/projects/errors.ts:1-40`
- **PATTERN**: Extend base Error, include code and statusCode
- **VALIDATE**: `npx tsc --noEmit`

### `[ ]` Task 5: CREATE `src/features/new/repository.ts`

- **ACTION**: CREATE database operations
- **IMPLEMENT**: findById, findByUserId, create, update, delete
- **MIRROR**: `src/features/projects/repository.ts:1-60`
- **IMPORTS**: `import { db } from "@/core/database/client"`
- **GOTCHA**: Use `results[0]` pattern, not `.first()` - check noUncheckedIndexedAccess
- **VALIDATE**: `npx tsc --noEmit`

### `[ ]` Task 6: CREATE `src/features/new/service.ts`

- **ACTION**: CREATE business logic layer
- **IMPLEMENT**: createThing, getThing, updateThing, deleteThing
- **MIRROR**: `src/features/projects/service.ts:1-80`
- **PATTERN**: Use repository, add logging, throw custom errors
- **IMPORTS**: `import { getLogger } from "@/core/logging"`
- **VALIDATE**: `{type-check-cmd} && {lint-cmd}`

### `[ ]` Task 7: CREATE `{source-dir}/features/new/index.ts`

- **ACTION**: CREATE public API exports
- **IMPLEMENT**: Export types, schemas, errors, service functions
- **MIRROR**: `{source-dir}/features/{example}/index.ts:1-20`
- **PATTERN**: Named exports only, hide repository (internal)
- **VALIDATE**: `{type-check-cmd}`

### `[ ]` Task 8: CREATE `{source-dir}/features/new/tests/service.test.ts`

- **ACTION**: CREATE unit tests for service
- **IMPLEMENT**: Test each service function, happy path + error cases
- **MIRROR**: `{source-dir}/features/{example}/tests/service.test.ts:1-100`
- **PATTERN**: Use project's test framework (jest, vitest, bun:test, pytest, etc.)
- **VALIDATE**: `{test-cmd} {path-to-tests}`
