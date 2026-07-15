# Comprehensive PR Review with Specialized Agents

> **Arguments:** `$ARGUMENTS` (and `$1`, `$2`, ...) refer to the arguments given when this skill was invoked. Take them from the user's request; if absent, infer them from the conversation.

Run a multi-agent review on a pull request, with each agent focusing on a specific aspect of code quality. This is the `--agents` mode of `prp-review`.

**Target**: $ARGUMENTS

## Pre-Review Setup

Before running reviews:

1. **Identify the PR**
   - If PR number provided: `gh pr view <number>`
   - If no number: `gh pr view` (current branch's PR)
   - Get PR branch name and changed files

2. **Check PR State**
   - Is rebase needed? Check if behind base branch
   - Are there conflicts? Resolve intelligently if needed
   - Never push to main without explicit user approval

3. **Get Changed Files**
   ```bash
   gh pr diff <number> --name-only
   ```

## Review Aspects

| Aspect | Agent | When to Run |
|--------|-------|-------------|
| `code` | code-reviewer | Always - general quality and guidelines |
| `docs` | docs-impact-agent | Almost always - identifies stale docs |
| `tests` | pr-test-analyzer | When test files or tested code changed |
| `comments` | comment-analyzer | When comments/docstrings added |
| `errors` | silent-failure-hunter | When error handling changed |
| `types` | type-design-analyzer | When types added/modified |
| `simplify` | code-simplifier | When `all` or `simplify` requested - advisory polish |
| `all` | All applicable | Default if no aspects specified |

## Aspect Selection Logic

**Always run**:
- `code-reviewer` - Core quality check

**Almost always run** (skip only for trivial PRs):
- `docs-impact-agent` - Identifies stale or missing docs

**Skip docs-impact-agent only when**:
- Typo-only fixes (comments, strings)
- Test-only changes (no production code)
- Documentation-only changes
- Config tweaks (CI, linting)

**Run based on changes**:
- Test files changed → `pr-test-analyzer`
- Comments/docstrings added → `comment-analyzer`
- Try-catch or error handling → `silent-failure-hunter`
- New types or type modifications → `type-design-analyzer`

**Include when in scope** (`all` or `simplify` requested):
- `code-simplifier` - Advisory polish; runs in the same parallel batch as the others

## Execution

Run in two steps: **decide which agents apply, then dispatch them in parallel.**

### Step 1 — Decide which agents apply

Using the Aspect Selection Logic above (and any aspects passed in `$ARGUMENTS`), build the final list of agents to run:

- Always include `code-reviewer`.
- Add `docs-impact-agent` unless the PR is trivial (see skip rules).
- Add change-based specialists (`pr-test-analyzer`, `comment-analyzer`, `silent-failure-hunter`, `type-design-analyzer`) based on what the diff touches.
- Include `code-simplifier` when `all` or `simplify` is in scope.

### Step 2 — Launch all selected agents in parallel (default)

Dispatch **every** selected agent as **parallel subagents spawned in one step** so they run concurrently. Do not run them one at a time.

- All agents are advisory and analyze the same git diff, so they have no ordering dependencies — there is no reason to serialize them.
- Wait for all agents to return, then aggregate their findings (see Result Aggregation).

### Sequential (opt-in only)

Run agents one at a time **only if the user explicitly asks for "sequential"** — e.g., to step through a single aspect for debugging.

## Agent Instructions

When spawning each subagent:

**code-reviewer**:
> Review PR #<number> for project guideline compliance, bugs, and quality issues. Focus on the diff. Report only high-confidence issues (80+).

**docs-impact-agent**:
> Review PR #<number> and identify any documentation affected by these changes. Check CLAUDE.md, README.md, and docs/ for stale, incorrect, or missing content. Report findings with specific file locations and suggested fixes. Do not modify files or commit.

**pr-test-analyzer**:
> Analyze test coverage for PR #<number>. Focus on behavioral coverage, identify critical gaps, rate recommendations by criticality.

**comment-analyzer**:
> Analyze code comments in PR #<number> for accuracy, completeness, and long-term value. Verify comments match actual code behavior.

**silent-failure-hunter**:
> Hunt for silent failures in PR #<number>. Check all error handling for proper logging, user feedback, and specific catch blocks.

**type-design-analyzer**:
> Analyze type design in PR #<number>. Rate encapsulation, invariant expression, usefulness, and enforcement. Focus on new or modified types.

**code-simplifier**:
> Identify simplification opportunities in PR #<number> for clarity while preserving functionality. No nested ternaries, prefer explicit over clever. Report findings with before/after suggestions. Do not modify files or commit.

## Result Aggregation

After all agents complete, aggregate findings into the canonical summary format.

**MANDATORY READ**: `../templates/review-report.md` — use its Categories and Summary Format exactly. Do not improvise a different shape.

## Write Local Report

**Always write the aggregated summary to a local file** (same artifact contract as single-pass mode):

```bash
mkdir -p .claude/PRPs/reviews
```

**Path**: `.claude/PRPs/reviews/pr-{NUMBER}-review.md`

## Post to GitHub

**Always post the summary to the PR when a PR number is provided**:

```bash
gh pr comment <PR_NUMBER> --body-file .claude/PRPs/reviews/pr-<PR_NUMBER>-review.md
```

## Usage Examples

```bash
# Full multi-agent review of specific PR
$prp-review 163 --agents

# Review only specific aspects
$prp-review 163 --agents tests errors

# Review current branch's PR
$prp-review --agents

# Only code and docs review
$prp-review 42 --agents code docs

# Force one-at-a-time execution (parallel is the default)
$prp-review 42 --agents all sequential

# Just simplify after passing review
$prp-review 42 --agents simplify
```

## Workflow Integration

**Before creating PR**:
1. Run `$prp-review --agents` on current branch
2. Fix critical and important issues
3. Re-run to verify
4. Create PR

**During PR review**:
1. Run `$prp-review <pr-number> --agents`
2. Review posts summary to GitHub
3. Address feedback
4. Re-run targeted aspects

**After making changes**:
1. Run specific aspects: `$prp-review <pr-number> --agents tests code`
2. Verify issues resolved
3. Push updates

## Notes

- Agents analyze git diff by default (changed files only)
- Each agent returns detailed report with file:line references
- All agents are advisory — they report findings but do not modify files or commit
- Summary always written to `.claude/PRPs/reviews/pr-{NUMBER}-review.md`, and posted as PR comment when PR number provided
