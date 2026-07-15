---
name: prp-plan
description: Create comprehensive feature implementation plan with codebase analysis and research. Also wires bidirectional back/forward references between existing plans (the update-references workflow). Use when the user wants to plan a feature, turn a PRD into an implementation plan, "link two plans", "add a back/forward reference", "connect related plans", or invokes $prp-plan.
---

> **Arguments:** `$ARGUMENTS` (and `$1`, `$2`, ...) refer to the arguments given when this skill was invoked. Take them from the user's request; if absent, infer them from the conversation.

<objective>
Transform "$ARGUMENTS" into a battle-tested implementation plan through systematic codebase exploration, pattern extraction, and strategic research.

**Core Principle**: PLAN ONLY - no code written. Create a context-rich document that enables one-pass implementation success.

**Execution Order**: CODEBASE FIRST, RESEARCH SECOND. Solutions must fit existing patterns before introducing new ones.

**Agent Strategy**: Use specialized agents for intelligence gathering:
- `codebase-explorer` — finds WHERE code lives and extracts implementation patterns
- `codebase-analyst` — analyzes HOW integration points work and traces data flow
- `web-researcher` — strategic web research with citations and gap analysis

Launch codebase agents in parallel first, then research agent second.
</objective>

<context>
Project rules: follow the loaded AGENTS.md context; also read CLAUDE.md if the project has one.

**Directory Discovery** (run these to understand project structure):
- List root contents: `ls -la`
- Find main source directories: `ls -la */ 2>/dev/null | head -50`
- Identify project type from config files (package.json, pyproject.toml, Cargo.toml, go.mod, etc.)

**IMPORTANT**: Do NOT assume `src/` exists. Common alternatives include:
- `app/` (Next.js, Rails, Laravel)
- `lib/` (Ruby gems, Elixir)
- `packages/` (monorepos)
- `cmd/`, `internal/`, `pkg/` (Go)
- Root-level source files (Python, scripts)

Discover the actual structure before proceeding.
</context>

<process>

## Mode Select

Before planning, check intent:

- **Link / connect two existing plans** — the request is to wire a back/forward reference between plans (e.g. "link plan A to plan B", "this plan builds on that one", `update-references <plan> <related> [back|forward]`). → Follow `workflows/update-references.md` and stop. Do NOT run the planning phases below.
- **Create / update a plan** (the default) — anything that describes a feature, hands over a PRD, or otherwise asks for an implementation plan. → Continue with Phase 0 below.

---

## Phase 0: DETECT - Input Type Resolution

**Determine input type:**

| Input Pattern | Type | Action |
|---------------|------|--------|
| Ends with `.prd.md` | PRD file | Parse PRD, select next phase |
| Ends with `.md` and contains "Implementation Phases" | PRD file | Parse PRD, select next phase |
| File path that exists | Document | Read and extract feature description |
| Free-form text | Description | Use directly as feature input |
| Empty/blank | Conversation | Use conversation context as input |

### If PRD File Detected:

1. **Read the PRD file**
2. **Parse the Implementation Phases table** - find rows with `Status: pending`
3. **Check dependencies** - only select phases whose dependencies are `complete`
4. **Select the next actionable phase:**
   - First pending phase with all dependencies complete
   - If multiple candidates with same dependencies, note parallelism opportunity

5. **Extract phase context:**
   ```
   PHASE: {phase number and name}
   GOAL: {from phase details}
   SCOPE: {from phase details}
   SUCCESS SIGNAL: {from phase details}
   PRD CONTEXT: {problem statement, user, hypothesis from PRD}
   ```

6. **Report selection to user:**
   ```
   PRD: {prd file path}
   Selected Phase: #{number} - {name}

   {If parallel phases available:}
   Note: Phase {X} can also run in parallel (in separate worktree).

   Proceeding with Phase #{number}...
   ```

### If Free-form or Conversation Context:

- Proceed directly to Phase 1 with the input as feature description

**PHASE_0_CHECKPOINT:**
- [ ] Input type determined
- [ ] If PRD: next phase selected and dependencies verified
- [ ] Feature description ready for Phase 1

---

## Phase 1: PARSE - Feature Understanding

**EXTRACT from input:**

- Core problem being solved
- User value and business impact
- Feature type: NEW_CAPABILITY | ENHANCEMENT | REFACTOR | BUG_FIX
- Complexity: LOW | MEDIUM | HIGH
- Affected systems list

**FORMULATE user story:**

```
As a <user type>
I want to <action/goal>
So that <benefit/value>
```

**PHASE_1_CHECKPOINT:**

- [ ] Problem statement is specific and testable
- [ ] User story follows correct format
- [ ] Complexity assessment has rationale
- [ ] Affected systems identified

**GATE**: If requirements are AMBIGUOUS → STOP and ASK user for clarification before proceeding.

---

## Phase 2: EXPLORE - Codebase Intelligence

**CRITICAL: Launch two specialized agents in parallel by spawning them as subagents in one step.** Read `references/agent-prompts.md` now (mandatory) — it is the exact prompt text for every subagent launch in Phases 2, 3, and 5.

- **Agent 1: `codebase-explorer`** — finds WHERE code lives and extracts implementation patterns. Launch with the Phase 2 codebase-explorer prompt.
- **Agent 2: `codebase-analyst`** — analyzes HOW integration points work and traces data flow. Launch with the Phase 2 codebase-analyst prompt.

### Merge Agent Results

Combine findings from both agents into a unified discovery table:

| Category | File:Lines                                  | Pattern Description  | Code Snippet                              |
| -------- | ------------------------------------------- | -------------------- | ----------------------------------------- |
| NAMING   | `src/features/X/service.ts:10-15`           | camelCase functions  | `export function createThing()`           |
| ERRORS   | `src/features/X/errors.ts:5-20`             | Custom error classes | `class ThingNotFoundError`                |
| LOGGING  | `src/core/logging/index.ts:1-10`            | getLogger pattern    | `const logger = getLogger("domain")`      |
| TESTS    | `src/features/X/tests/service.test.ts:1-30` | describe/it blocks   | `describe("service", () => {`             |
| TYPES    | `src/features/X/models.ts:1-20`             | Drizzle inference    | `type Thing = typeof things.$inferSelect` |
| FLOW     | `src/features/X/service.ts:40-60`           | Data transformation  | `input → validate → persist → respond`    |

**PHASE_2_CHECKPOINT:**

- [ ] Both agents (`codebase-explorer` and `codebase-analyst`) launched in parallel and completed
- [ ] At least 3 similar implementations found with file:line refs
- [ ] Code snippets are ACTUAL (copy-pasted from codebase, not invented)
- [ ] Integration points mapped with data flow traces
- [ ] Dependencies cataloged with versions from package.json

---

## Phase 3: RESEARCH - External Documentation

**ONLY AFTER Phase 2 is complete** - solutions must fit existing codebase patterns first.

**Launch `web-researcher`** with the Phase 3 web-researcher prompt from `references/agent-prompts.md`, filling in the feature description and the dependency versions found in Phase 2.

**FORMAT the agent's findings into plan references:**

```markdown
- [Library Docs v{version}](https://url#specific-section)
  - KEY_INSIGHT: {what we learned that affects implementation}
  - APPLIES_TO: {which task/file this affects}
  - GOTCHA: {potential pitfall and how to avoid}
```

**PHASE_3_CHECKPOINT:**

- [ ] `web-researcher` agent launched and completed
- [ ] Documentation versions match package.json
- [ ] URLs include specific section anchors (not just homepage)
- [ ] Gotchas documented with mitigation strategies
- [ ] No conflicting patterns between external docs and existing codebase

---

## Phase 4: DESIGN - UX Transformation

**CREATE ASCII diagrams showing user experience before and after, then DOCUMENT interaction changes.** Read `templates/ux-diagram-format.md` now (mandatory) — it is the exact BEFORE/AFTER diagram shape and interaction-changes table to produce.

**PHASE_4_CHECKPOINT:**

- [ ] Before state accurately reflects current system behavior
- [ ] After state shows ALL new capabilities
- [ ] Data flows are traceable from input to output
- [ ] User value is explicit and measurable

---

## Phase 5: ARCHITECT - Strategic Design

**For complex features with multiple integration points**, use `codebase-analyst` to trace how existing architecture works at the integration points identified in Phase 2 — launch with the Phase 5 architecture deep-dive prompt from `references/agent-prompts.md`.

**Then ANALYZE deeply (use extended thinking if needed):**

- ARCHITECTURE_FIT: How does this integrate with the existing architecture?
- EXECUTION_ORDER: What must happen first → second → third?
- FAILURE_MODES: Edge cases, race conditions, error scenarios?
- PERFORMANCE: Will this scale? Database queries optimized?
- SECURITY: Attack vectors? Data exposure risks? Auth/authz?
- MAINTAINABILITY: Will future devs understand this code?

**DECIDE and document:**

```markdown
APPROACH_CHOSEN: [description]
RATIONALE: [why this over alternatives - reference codebase patterns]

ALTERNATIVES_REJECTED:

- [Alternative 1]: Rejected because [specific reason]
- [Alternative 2]: Rejected because [specific reason]

NOT_BUILDING (explicit scope limits):

- [Item 1 - explicitly out of scope and why]
- [Item 2 - explicitly out of scope and why]
```

**PHASE_5_CHECKPOINT:**

- [ ] Approach aligns with existing architecture and patterns
- [ ] Dependencies ordered correctly (types → repository → service → routes)
- [ ] Edge cases identified with specific mitigation strategies
- [ ] Scope boundaries are explicit and justified

---

## Phase 6: GENERATE - Implementation Plan File

**OUTPUT_PATH**: `.claude/PRPs/plans/{kebab-case-feature-name}.plan.md`

Create directory if needed: `mkdir -p .claude/PRPs/plans`

**PLAN_STRUCTURE**: Read `templates/plan-template.md` now (mandatory) — it is the exact plan document to fill and save. Keep every section heading; fill every `{placeholder}` with real, project-specific content (the template's remaining snippets and table entries are illustrative examples from one TypeScript project, not content to keep). Before writing the plan's Step-by-Step Tasks section, read `references/task-block-format.md` (mandatory) for the task-block field detail and worked examples; before filling its Validation Commands section, read `references/validation-commands.md` (mandatory) for the per-language commands to embed.

</process>

<output>
**OUTPUT_FILE**: `.claude/PRPs/plans/{kebab-case-feature-name}.plan.md`

**If input was from PRD file**, also update the PRD:

1. **Update phase status** in the Implementation Phases table:
   - Change the phase's Status from `pending` to `in-progress`
   - Add the plan file path to the PRP Plan column

2. **Edit the PRD file** with these changes

**REPORT_TO_USER** (display after creating plan): Read `templates/report-format.md` now (mandatory) and display the "Plan Created" report in exactly that structure.

</output>

<verification>
**FINAL_VALIDATION before saving plan:**

**CONTEXT_COMPLETENESS:**

- [ ] All patterns from `codebase-explorer` and `codebase-analyst` documented with file:line references
- [ ] External docs versioned to match package.json
- [ ] Integration points mapped with specific file paths
- [ ] Gotchas captured with mitigation strategies
- [ ] Every task has at least one executable validation command

**IMPLEMENTATION_READINESS:**

- [ ] Tasks ordered by dependency (can execute top-to-bottom)
- [ ] Each task is atomic and independently testable
- [ ] No placeholders - all content is specific and actionable
- [ ] Pattern references include actual code snippets (copy-pasted, not invented)

**PATTERN_FAITHFULNESS:**

- [ ] Every new file mirrors existing codebase style exactly
- [ ] No unnecessary abstractions introduced
- [ ] Naming follows discovered conventions
- [ ] Error/logging patterns match existing
- [ ] Test structure matches existing tests

**VALIDATION_COVERAGE:**

- [ ] Every task has executable validation command
- [ ] All 6 validation levels defined where applicable
- [ ] Edge cases enumerated with test plans

**UX_CLARITY:**

- [ ] Before/After ASCII diagrams are detailed and accurate
- [ ] Data flows are traceable
- [ ] User value is explicit and measurable

**NO_PRIOR_KNOWLEDGE_TEST**: Could an agent unfamiliar with this codebase implement using ONLY the plan?
</verification>

<success_criteria>
**CONTEXT_COMPLETE**: All patterns, gotchas, integration points documented from actual codebase via `codebase-explorer` and `codebase-analyst` agents
**IMPLEMENTATION_READY**: Tasks executable top-to-bottom without questions, research, or clarification
**PATTERN_FAITHFUL**: Every new file mirrors existing codebase style exactly
**VALIDATION_DEFINED**: Every task has executable verification command
**UX_DOCUMENTED**: Before/After transformation is visually clear with data flows
**ONE_PASS_TARGET**: Confidence score 8+ indicates high likelihood of first-attempt success
</success_criteria>

## Resources

- `references/agent-prompts.md` — exact subagent prompts for Phases 2, 3, and 5 (mandatory read at Phase 2)
- `templates/plan-template.md` — the plan document to fill and save (mandatory read in Phase 6)
- `templates/ux-diagram-format.md` — the BEFORE/AFTER ASCII diagram shape and interaction-changes table (mandatory read in Phase 4)
- `templates/report-format.md` — the "Plan Created" report displayed to the user (mandatory read in Output)
- `references/task-block-format.md` — task-block field detail and worked examples (mandatory read in Phase 6, before writing Step-by-Step Tasks)
- `references/validation-commands.md` — per-language validation command catalog (mandatory read in Phase 6, before filling Validation Commands)
- `workflows/update-references.md` — the update-references mode (read only when Mode Select routes there)
