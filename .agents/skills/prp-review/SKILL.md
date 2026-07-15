---
name: prp-review
description: Comprehensive PR code review - checks diff, patterns, runs validation, comments on PR. Single-pass by default; pass --agents for a multi-agent specialist fan-out (comments, tests, errors, types, code, docs, simplify). Use when the user wants to review a pull request, wants a thorough/multi-agent review, or invokes $prp-review.
---

> **Arguments:** `$ARGUMENTS` (and `$1`, `$2`, ...) refer to the arguments given when this skill was invoked. Take them from the user's request; if absent, infer them from the conversation.

# PR Code Review

**Input**: $ARGUMENTS

---

## Mode Select

This skill has two modes:

| Mode | Trigger | What it does |
|------|---------|--------------|
| **Single-pass** (default) | no `--agents` flag | One reviewer performs the full 8-phase review below |
| **Multi-agent fan-out** | `--agents` flag present, or aspect keywords (`comments`/`tests`/`errors`/`types`/`code`/`docs`/`simplify`/`all`), or the user asks for a "multi-agent"/"thorough" review | Dispatches specialized agents in parallel, one per aspect |

**If multi-agent mode is selected**: follow `workflows/agents.md` instead of the phases below, then stop. Everything below this section is the single-pass review.

Single-pass is the cheaper default; reach for `--agents` on large diffs or when explicitly asked.

---

## Your Mission

Perform a thorough, senior-engineer-level code review:

1. **Understand** what the PR is trying to accomplish
2. **Check** the code against project patterns and constraints
3. **Run** all validation (type-check, lint, tests, build)
4. **Identify** issues by category (Critical / Important / Suggestions / Strengths)
5. **Report** findings as PR comment AND local file

**Golden Rule**: Be constructive and actionable. Every issue should have a clear recommendation. Acknowledge good work too.

---

## Phase 1: FETCH - Get PR Context

### 1.1 Parse Input

**Determine input type:**

| Input Format | Action |
|--------------|--------|
| Number (`123`, `#123`) | Use as PR number |
| URL (`https://github.com/.../pull/123`) | Extract PR number |
| Branch name (`feature-x`) | Find associated PR |

```bash
# If branch name provided, find PR
gh pr list --head {branch-name} --json number -q '.[0].number'
```

### 1.2 Get PR Metadata

```bash
# Get comprehensive PR details
gh pr view {NUMBER} --json number,title,body,author,headRefName,baseRefName,state,additions,deletions,changedFiles,files,reviews,comments

# Get the diff
gh pr diff {NUMBER}

# List changed files
gh pr diff {NUMBER} --name-only
```

**Extract:**
- PR number, title, description
- Author
- Base and head branches
- Files changed with line counts
- Existing review comments

### 1.3 Checkout PR Branch

```bash
# Fetch and checkout the PR branch
gh pr checkout {NUMBER}
```

### 1.4 Validate PR State

| State | Action |
|-------|--------|
| `MERGED` | STOP: "PR already merged. Nothing to review." |
| `CLOSED` | WARN: "PR is closed. Review anyway? (historical analysis)" |
| `DRAFT` | NOTE: "Draft PR - focusing on direction, not polish" |
| `OPEN` | PROCEED with full review |

**PHASE_1_CHECKPOINT:**
- [ ] PR number identified
- [ ] PR metadata fetched
- [ ] PR branch checked out
- [ ] PR state is reviewable

---

## Phase 2: CONTEXT - Understand the Change

### 2.1 Read Project Rules

Read and internalize:

```bash
# Project conventions
cat CLAUDE.md

# Check for additional reference docs
ls -la .claude/docs/ 2>/dev/null
ls -la docs/ 2>/dev/null
```

**Extract key constraints:**
- Type safety requirements
- Code style rules
- Testing requirements
- Architecture patterns

### 2.2 Find Implementation Context

Look for implementation artifacts:

```bash
# Find implementation report by branch name
ls .claude/PRPs/reports/*{branch-name}*.md 2>/dev/null

# Find completed plans
ls .claude/PRPs/plans/completed/ 2>/dev/null

# Find issue investigations
ls .claude/PRPs/issues/completed/ 2>/dev/null
```

**If implementation report exists:**
1. Read the implementation report
2. Read the referenced plan
3. Note documented deviations - these are INTENTIONAL, not issues

**If no implementation report:**
- PR may not have been created via `$prp-implement`
- Review normally without plan context
- Note in review that no implementation report was found

### 2.3 Understand PR Intent

From PR title, description, AND implementation report (if available):
- What problem does this solve?
- What approach was taken?
- Are there notes from the author?
- What deviations from plan were documented and why?

### 2.4 Analyze Changed Files

For each changed file, determine:
- What type of file? (service, handler, util, test, config)
- What existing patterns should it follow?
- Scope of change? (new file, modification, deletion)

**PHASE_2_CHECKPOINT:**
- [ ] Project rules read and understood
- [ ] Implementation artifacts located (if any)
- [ ] PR intent understood
- [ ] Changed files categorized

---

## Phase 3: REVIEW - Analyze the Code

### 3.1 Read Each Changed File

For each file in the diff:

1. **Read the full file** (not just diff) to understand context
2. **Read similar files** to understand expected patterns
3. **Check specific changes** against patterns

### 3.2 Review Checklist

**For EVERY changed file, check:**

#### Correctness
- [ ] Does the code do what the PR claims?
- [ ] Are there logic errors?
- [ ] Are edge cases handled?
- [ ] Is error handling appropriate?

#### Type Safety
- [ ] Are all types explicit (no implicit `any`)?
- [ ] Are return types declared?
- [ ] Are interfaces used appropriately?
- [ ] Are type guards used where needed?

#### Pattern Compliance
- [ ] Does it follow existing patterns in the codebase?
- [ ] Is naming consistent with project conventions?
- [ ] Is file organization correct?
- [ ] Are imports from the right places?

#### Security
- [ ] Any user input without validation?
- [ ] Any secrets that could be exposed?
- [ ] Any injection vulnerabilities (SQL, command, etc.)?
- [ ] Any unsafe operations?

#### Performance
- [ ] Any obvious N+1 queries or loops?
- [ ] Any unnecessary async/await?
- [ ] Any memory leaks (unclosed resources, growing arrays)?
- [ ] Any blocking operations in hot paths?

#### Completeness
- [ ] Are there tests for new code?
- [ ] Is documentation updated if needed?
- [ ] Are all TODOs addressed?
- [ ] Is error handling complete?

#### Maintainability
- [ ] Is the code readable?
- [ ] Is it over-engineered?
- [ ] Is it under-engineered (missing necessary abstractions)?
- [ ] Are there magic numbers/strings that should be constants?

### 3.3 Categorize Issues

**Important: Check implementation report first!**

If a deviation from expected patterns is documented in the implementation report with a valid reason, it is NOT an issue - it's an intentional decision. Only flag **undocumented** deviations.

**Finding Categories** (shared with `--agents` mode — see `templates/review-report.md`):

| Category | Icon | Criteria | Examples |
|----------|------|----------|----------|
| Critical | `RED` | Must fix before merge - blocking | Security vulnerabilities, data loss potential, crashes |
| Important | `ORANGE` | Should fix before merge | Type safety violations, missing error handling, logic errors |
| Suggestions | `YELLOW` | Nice to have - consider | Pattern inconsistencies, missing edge cases, undocumented deviations, style preferences, minor optimizations, documentation |
| Strengths | `GREEN` | What's good - acknowledge | Good patterns, clean code, thorough tests |

**PHASE_3_CHECKPOINT:**
- [ ] All changed files reviewed
- [ ] Issues categorized
- [ ] Implementation report deviations accounted for
- [ ] Positive aspects noted

---

## Phase 4: VALIDATE - Run Automated Checks

### 4.1 Run Validation Suite

```bash
# Type checking (adapt to project)
npm run type-check || bun run type-check || npx tsc --noEmit

# Linting
npm run lint || bun run lint

# Tests
npm test || bun test

# Build
npm run build || bun run build
```

**Capture for each:**
- Pass/fail status
- Error count
- Warning count
- Any specific failures

### 4.2 Specific Validation

Based on what changed:

| Change Type | Additional Validation |
|-------------|----------------------|
| New API endpoint | Test with curl/httpie |
| Database changes | Check migration exists |
| Config changes | Verify .env.example updated |
| New dependencies | Check package.json/lock file |

### 4.3 Regression Check

```bash
# Full test suite
npm test || bun test

# Specific tests for changed functionality
npm test -- {relevant-test-pattern}
```

**PHASE_4_CHECKPOINT:**
- [ ] Type check executed
- [ ] Lint executed
- [ ] Tests executed
- [ ] Build executed
- [ ] Results captured

---

## Phase 5: DECIDE - Form Recommendation

### 5.1 Decision Logic

**APPROVE** if:
- No Critical or Important issues
- All validation passes
- Code follows patterns
- Changes match PR intent

**REQUEST CHANGES** if:
- Important issues exist
- Validation fails but is fixable
- Pattern violations that need addressing
- Missing tests for new functionality

**BLOCK** if:
- Critical security or data issues
- Fundamental approach is wrong
- Major architectural concerns
- Breaking changes without migration

### 5.2 Special Cases

| Situation | Handling |
|-----------|----------|
| Draft PR | Comment only, no approve/block |
| Large PR (>500 lines) | Note thoroughness limits, suggest splitting |
| Security-sensitive | Extra scrutiny, err on caution |
| Missing tests | Strong recommendation, may not block |

**PHASE_5_CHECKPOINT:**
- [ ] Recommendation determined
- [ ] Rationale clear

---

## Phase 6: REPORT - Generate Review

### 6.1 Create Report Directory

```bash
mkdir -p .claude/PRPs/reviews
```

### 6.2 Generate Report File

**Path**: `.claude/PRPs/reviews/pr-{NUMBER}-review.md`

```markdown
---
pr: {NUMBER}
title: "{TITLE}"
author: "{AUTHOR}"
reviewed: {ISO_TIMESTAMP}
recommendation: {approve|request-changes|block}
---

# PR Review: #{NUMBER} - {TITLE}

**Author**: @{author}
**Branch**: {head} -> {base}
**Files Changed**: {count} (+{additions}/-{deletions})

---

## Summary

{2-3 sentences: What this PR does and overall assessment}

---

## Implementation Context

| Artifact | Path |
|----------|------|
| Implementation Report | `{path}` or "Not found" |
| Original Plan | `{path}` or "Not found" |
| Documented Deviations | {count} or "N/A" |

{If implementation report exists: Brief note about deviation documentation quality}

---

## Changes Overview

| File | Changes | Assessment |
|------|---------|------------|
| `{path/to/file.ts}` | +{N}/-{M} | {PASS/WARN/FAIL} |

---

## Issues Found

### Critical
{If none: "No critical issues found."}

- **`{file.ts}:{line}`** - {Issue description}
  - **Why**: {Explanation of the problem}
  - **Fix**: {Specific recommendation}

### Important
{Issues that should be fixed before merge}

### Suggestions
{Issues worth considering but not blocking, nice-to-haves, and future improvements}

---

## Validation Results

| Check | Status | Details |
|-------|--------|---------|
| Type Check | {PASS/FAIL} | {notes} |
| Lint | {PASS/WARN} | {count} warnings |
| Tests | {PASS/FAIL} | {count} passed |
| Build | {PASS/FAIL} | {notes} |

---

## Pattern Compliance

- [{x}] Follows existing code structure
- [{x}] Type safety maintained
- [{x}] Naming conventions followed
- [{x}] Tests added for new code
- [{x}] Documentation updated

---

## Strengths

{Acknowledge positive aspects - good patterns, clean code, thorough tests, etc.}

---

## Recommendation

**{APPROVE/REQUEST CHANGES/BLOCK}**

{Clear explanation of recommendation and what needs to happen next}

---

*Reviewed by Claude*
*Report: `.claude/PRPs/reviews/pr-{NUMBER}-review.md`*
```

**PHASE_6_CHECKPOINT:**
- [ ] Report file created
- [ ] All sections populated

---

## Phase 7: PUBLISH - Post to GitHub

### 7.1 Determine Review Action

Based on recommendation and flags:

```bash
# If --approve flag AND no Critical/Important issues
gh pr review {NUMBER} --approve --body-file .claude/PRPs/reviews/pr-{NUMBER}-review.md

# If --request-changes flag OR Important issues found
gh pr review {NUMBER} --request-changes --body-file .claude/PRPs/reviews/pr-{NUMBER}-review.md

# Otherwise just comment
gh pr comment {NUMBER} --body-file .claude/PRPs/reviews/pr-{NUMBER}-review.md
```

### 7.2 Get Comment URL

```bash
# Get the review/comment URL
gh pr view {NUMBER} --json reviews,comments --jq '.reviews[-1].url // .comments[-1].url'
```

**PHASE_7_CHECKPOINT:**
- [ ] Review/comment posted to PR
- [ ] Comment URL captured

---

## Phase 8: OUTPUT - Report to User

```markdown
## PR Review Complete

**PR**: #{NUMBER} - {TITLE}
**URL**: {PR_URL}
**Recommendation**: {APPROVE/REQUEST CHANGES/BLOCK}

### Issues Found

| Category | Count |
|----------|-------|
| Critical | {N} |
| Important | {N} |
| Suggestions | {N} |

### Validation

| Check | Result |
|-------|--------|
| Type Check | {PASS/FAIL} |
| Lint | {PASS/FAIL} |
| Tests | {PASS/FAIL} |
| Build | {PASS/FAIL} |

### Artifacts

- Report: `.claude/PRPs/reviews/pr-{NUMBER}-review.md`
- PR Comment: {comment_url}

### Next Steps

{Based on recommendation:}
- APPROVE: "PR is ready for merge"
- REQUEST CHANGES: "Author should address {N} Important issues"
- BLOCK: "Fundamental issues need resolution before proceeding"
```

---

## Critical Reminders

1. **Understand before judging.** Read full context, not just the diff.

2. **Be specific.** "This could be better" is useless. "Use `execFile` instead of `exec` to prevent command injection at line 45" is helpful.

3. **Prioritize.** Not everything is critical. Use the categories honestly.

4. **Be constructive.** Offer solutions, not just problems.

5. **Acknowledge good work.** If something is done well, say so.

6. **Run validation.** Don't skip automated checks.

7. **Check patterns.** Read existing similar code to understand expectations.

8. **Think about edge cases.** What happens with null, empty, very large, concurrent?

9. **Check implementation report.** Documented deviations are intentional, not issues.

---

## Success Criteria

- **CONTEXT_GATHERED**: PR metadata, diff, and implementation artifacts reviewed
- **CODE_REVIEWED**: All changed files analyzed against checklist
- **VALIDATION_RUN**: All automated checks executed
- **ISSUES_CATEGORIZED**: Findings organized by category
- **REPORT_GENERATED**: Comprehensive review saved locally
- **PR_UPDATED**: Review/comment posted to GitHub
- **RECOMMENDATION_CLEAR**: Approve/request-changes/block with rationale
