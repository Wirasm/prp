# Implement Issue

> **Arguments:** `$ARGUMENTS` (and `$1`, `$2`, ...) refer to the arguments given when this skill was invoked. Take them from the user's request; if absent, infer them from the conversation.

**Input**: $ARGUMENTS

---

## Your Mission

Execute the implementation plan from `prp-issue investigate`:

1. Load and validate the artifact
2. Ensure git state is correct
3. Implement the changes exactly as specified
4. Run validation
5. Create PR linked to issue
6. Run self-review and post findings
7. Archive the artifact

**Golden Rule**: Follow the artifact. If something seems wrong, validate it first - don't silently deviate.

---

## Phase 0: DETECT - Base Branch

### 0.1 Detect Base Branch

Determine the base branch for branching, syncing, and PR creation:

1. **Check arguments**: If `$ARGUMENTS` contains `--base <branch>`, extract that value and remove the flag from the remaining arguments
2. **Auto-detect from remote**:
   ```bash
   git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'
   ```
3. **Fallback if detection fails**:
   ```bash
   git remote show origin 2>/dev/null | grep 'HEAD branch' | awk '{print $NF}'
   ```
4. **Last resort**: `main`

**Store as `{base-branch}`** — use this value for ALL branch comparisons, rebasing, syncing, and PR creation. Never hardcode `main` or `master`.

---

## Phase 1: LOAD - Get the Artifact

### 1.1 Determine Input Type

**If input looks like a number** (`123`, `#123`):

```bash
# Look for artifact
ls .claude/PRPs/issues/issue-{number}.md
```

**If input is a path**:

- Use the path directly

### 1.2 Load and Parse Artifact

```bash
cat {artifact-path}
```

**Extract from artifact:**

- Issue number and title
- Type (BUG/ENHANCEMENT/etc)
- Files to modify (with line numbers)
- Implementation steps
- Validation commands
- Test cases to add

### 1.3 Validate Artifact Exists

**If artifact not found:**

```
❌ Artifact not found at .claude/PRPs/issues/issue-{number}.md

Run `$prp-issue investigate {number}` first to create the implementation plan.
```

**PHASE_1_CHECKPOINT:**

- [ ] Artifact found and loaded
- [ ] Key sections parsed (files, steps, validation)
- [ ] Issue number extracted (if applicable)

---

## Phase 2: VALIDATE - Sanity Check

### 2.1 Verify Plan Accuracy

For each file mentioned in the artifact:

- Read the actual current code
- Compare to what artifact expects
- Check if the "current code" snippets match reality

**If significant drift detected:**

```
⚠️ Code has changed since investigation:

File: src/x.ts:45
- Artifact expected: {snippet}
- Actual code: {different snippet}

Options:
1. Re-run `prp-issue investigate` to get fresh analysis
2. Proceed carefully with manual adjustments
```

### 2.2 Confirm Approach Makes Sense

Ask yourself:

- Does the proposed fix actually address the root cause?
- Are there obvious problems with the approach?
- Has something changed that invalidates the plan?

**If plan seems wrong:**

- STOP
- Explain what's wrong
- Suggest re-investigation

**PHASE_2_CHECKPOINT:**

- [ ] Artifact matches current codebase state
- [ ] Approach still makes sense
- [ ] No blocking issues identified

---

## Phase 3: GIT-CHECK - Ensure Correct State

### 3.1 Check Current Git State

```bash
# What branch are we on?
git branch --show-current

# Are we in a worktree?
git rev-parse --show-toplevel
git worktree list

# Is working directory clean?
git status --porcelain

# Are we up to date with remote?
git fetch origin
git status
```

### 3.2 Decision Tree

```
┌─ IN WORKTREE?
│  └─ YES → Use it (assume it's for this work)
│           Log: "Using worktree at {path}"
│
├─ ON {base-branch}?
│  └─ Q: Working directory clean?
│     ├─ YES → Create branch: fix/issue-{number}-{slug}
│     │        git checkout -b fix/issue-{number}-{slug}
│     └─ NO  → Warn user:
│              "Working directory has uncommitted changes.
│               Please commit or stash before proceeding."
│              STOP
│
├─ ON FEATURE/FIX BRANCH?
│  └─ Use it (assume it's for this work)
│     If branch name doesn't contain issue number:
│       Warn: "Branch '{name}' may not be for issue #{number}"
│
└─ DIRTY STATE?
   └─ Warn and suggest: git stash or git commit
      STOP
```

### 3.3 Ensure Up-to-Date

```bash
# If branch tracks remote
git pull --rebase origin {base-branch} 2>/dev/null || git pull origin {base-branch}
```

**PHASE_3_CHECKPOINT:**

- [ ] Git state is clean and correct
- [ ] On appropriate branch (created or existing)
- [ ] Up to date with {base-branch}

---

## Phase 4: IMPLEMENT - Make Changes

### 4.1 Execute Each Step

For each step in the artifact's Implementation Plan:

1. **Read the target file** - understand current state
2. **Make the change** - exactly as specified
3. **Verify types compile** - run the project's type-check command

### 4.2 Implementation Rules

**DO:**

- Follow artifact steps in order
- Match existing code style exactly
- Copy patterns from "Patterns to Follow" section
- Add tests as specified

**DON'T:**

- Refactor unrelated code
- Add "improvements" not in the plan
- Change formatting of untouched lines
- Deviate from the artifact without noting it

### 4.3 Handle Each File Type

**For UPDATE files:**

- Read current content
- Find the exact lines mentioned
- Make the specified change
- Preserve surrounding code

**For CREATE files:**

- Use patterns from artifact
- Follow existing file structure conventions
- Include all specified content

**For test files:**

- Add test cases as specified
- Follow existing test patterns
- Ensure tests actually test the fix

### 4.4 Track Deviations

If you must deviate from the artifact:

- Note what changed and why
- Include in PR description

**PHASE_4_CHECKPOINT:**

- [ ] All steps from artifact executed
- [ ] Types compile after each change
- [ ] Tests added as specified
- [ ] Any deviations documented

---

## Phase 5: VERIFY - Run Validation

### 5.1 Run Artifact Validation Commands

Execute each command from the artifact's Validation section.

Common patterns (adapt to project's toolchain):
```bash
# Type check
{runner} run type-check  # or: mypy ., cargo check, go build ./...

# Tests
{runner} test {pattern-from-artifact}  # or: pytest, cargo test, go test

# Lint
{runner} run lint  # or: ruff check ., cargo clippy
```

### 5.2 Check Results

**All must pass before proceeding.**

If failures:

1. Analyze what's wrong
2. Fix the issue
3. Re-run validation
4. Note any fixes in PR description

### 5.3 Manual Verification (if specified)

Execute any manual verification steps from the artifact.

**PHASE_5_CHECKPOINT:**

- [ ] Type check passes
- [ ] Tests pass
- [ ] Lint passes
- [ ] Manual verification complete (if applicable)

---

## Phase 6: COMMIT - Save Changes

### 6.1 Stage Changes

```bash
# Stage specific changed files (prefer over git add -A)
git add {list of changed files}
git status  # Review what's being committed
```

### 6.2 Write Commit Message

**Format:**

```
Fix: {brief description} (#{issue-number})

{Problem statement from artifact - 1-2 sentences}

Changes:
- {Change 1 from artifact}
- {Change 2 from artifact}
- Added test for {case}

Fixes #{issue-number}
```

**Commit:**

```bash
git commit -m "$(cat <<'EOF'
Fix: {title} (#{number})

{problem statement}

Changes:
- {change 1}
- {change 2}

Fixes #{number}
EOF
)"
```

**PHASE_6_CHECKPOINT:**

- [ ] All changes committed
- [ ] Commit message references issue

---

## Phase 7: PR - Create Pull Request

### 7.1 Push to Remote

```bash
git push -u origin HEAD
```

If branch was rebased:

```bash
git push -u origin HEAD --force-with-lease
```

### 7.2 Create PR

````bash
gh pr create --base "{base-branch}" --title "Fix: {title} (#{number})" --body "$(cat <<'EOF'
## Summary

{Problem statement from artifact}

## Root Cause

{Root cause summary from artifact}

## Changes

| File | Change |
|------|--------|
| `src/x.ts` | {description} |
| `src/x.test.ts` | Added test for {case} |

## Testing

- [x] Type check passes
- [x] Unit tests pass
- [x] Lint passes
- [x] {Manual verification from artifact}

## Validation

```bash
# Run project's validation commands (adapt to toolchain)
{type-check-cmd} && {test-cmd} {pattern} && {lint-cmd}
```

## Issue

Fixes #{number}

---

<details>
<summary>📋 Implementation Details</summary>

### Implementation followed artifact:

`.claude/PRPs/issues/issue-{number}.md`

### Deviations from plan:

{None | List any deviations}

</details>

---

_Automated implementation from investigation artifact_
EOF
)"

````

### 7.3 Get PR Number

```bash
PR_URL=$(gh pr view --json url -q '.url')
PR_NUMBER=$(gh pr view --json number -q '.number')
```

**PHASE_7_CHECKPOINT:**

- [ ] Changes pushed to remote
- [ ] PR created
- [ ] PR linked to issue with "Fixes #{number}"

---

## Phase 8: REVIEW - Self Code Review

### 8.1 Run Self-Review Agents (in parallel)

Launch both agents as **two parallel subagents spawned in one step** so they run concurrently. Both are advisory and read the same diff — there is no reason to serialize them.

**code-reviewer** (spawn as the `code-reviewer` subagent):

```
Review the changes in this PR for issue #{number}.

Focus on:
1. Does the fix address the root cause from the investigation?
2. Code quality - matches codebase patterns?
3. Test coverage - are the new tests sufficient?
4. Edge cases - are they handled?
5. Security - any concerns?
6. Potential bugs - anything that could break?

Review only the diff, not the entire codebase.
```

**code-simplifier** (spawn as the `code-simplifier` subagent):

```
Identify simplification opportunities in the changes for issue #{number}.
Focus only on the diff. Prefer explicit over clever; no nested ternaries.
Report findings with before/after suggestions. Advisory only — do not modify files or commit.
```

### 8.2 Post Review to PR

```bash
gh pr comment --body "$(cat <<'EOF'
## 🔍 Automated Code Review

### Summary

{1-2 sentence assessment}

### Findings

#### ✅ Strengths
- {Good thing 1}
- {Good thing 2}

#### ⚠️ Suggestions (non-blocking)
- `{file}:{line}` - {suggestion}
- {other suggestions}

#### 🧹 Simplification (from code-simplifier)
- `{file}:{line}` - {simplification, or "No simplifications identified"}

#### 🔒 Security
- {Any concerns or "No security concerns identified"}

### Checklist

- [x] Fix addresses root cause from investigation
- [x] Code follows codebase patterns
- [x] Tests cover the change
- [x] No obvious bugs introduced

---
*Self-reviewed by Claude • Ready for human review*
EOF
)"
```

**PHASE_8_CHECKPOINT:**

- [ ] Code review + simplification completed (run in parallel)
- [ ] Review posted to PR

---

## Phase 9: ARCHIVE - Clean Up

### 9.1 Move Artifact to Completed

```bash
mkdir -p .claude/PRPs/issues/completed
mv .claude/PRPs/issues/issue-{number}.md .claude/PRPs/issues/completed/
```

### 9.2 Commit and Push Archive

```bash
git add .claude/PRPs/issues/
git commit -m "Archive investigation for issue #{number}"
git push
```

**PHASE_9_CHECKPOINT:**

- [ ] Artifact moved to completed folder
- [ ] Archive committed and pushed

---

## Phase 10: REPORT - Output to User

```markdown
## Implementation Complete

**Issue**: #{number} - {title}
**Branch**: `{branch-name}`
**PR**: #{pr-number} - {pr-url}

### Changes Made

| File            | Change        |
| --------------- | ------------- |
| `src/x.ts`      | {description} |
| `src/x.test.ts` | Added test    |

### Validation

| Check      | Result  |
| ---------- | ------- |
| Type check | ✅ Pass |
| Tests      | ✅ Pass |
| Lint       | ✅ Pass |

### Self-Review

{Summary of review findings}

### Artifact

📄 Archived to `.claude/PRPs/issues/completed/issue-{number}.md`

### Next Steps

- Human review of PR #{pr-number}
- Merge when approved
```

---

## Handling Edge Cases

### Artifact is outdated

- Warn user about drift
- Suggest re-running `prp-issue investigate`
- Can proceed with caution if changes are minor

### Tests fail after implementation

- Debug the failure
- Fix the code (not the test, unless test is wrong)
- Re-run validation
- Note the additional fix in PR

### Merge conflicts during rebase

- Resolve conflicts
- Re-run full validation
- Note conflict resolution in PR

### PR creation fails

- Check if PR already exists for branch
- Check for permission issues
- Provide manual gh command

### Already on a branch with changes

- Use the existing branch
- Warn if branch name doesn't match issue
- Don't create a new branch

### In a worktree

- Use it as-is
- Assume it was created for this purpose
- Log that worktree is being used

---

## Success Criteria

- **PLAN_EXECUTED**: All artifact steps completed
- **VALIDATION_PASSED**: All checks green
- **PR_CREATED**: PR exists and linked to issue
- **REVIEW_POSTED**: Self-review comment on PR
- **ARTIFACT_ARCHIVED**: Moved to completed folder
- **AUDIT_TRAIL**: Full history in git and GitHub
