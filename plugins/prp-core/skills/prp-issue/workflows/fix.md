# Implement Issue

**Input**: $ARGUMENTS

---

## Your Mission

Execute the implementation plan from `prp-issue investigate`:

1. Load and validate the artifact
2. Ensure git state is correct
3. Implement the changes exactly as specified
4. Run validation
5. Create PR linked to issue
6. Have the PR reviewed by the review agents, then act on what they report
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
# Look for the new store artifact first. A legacy hit requires migration.
if [ -f "$PRP_DIR/issues/issue-{number}.md" ]; then
  artifact_path="$PRP_DIR/issues/issue-{number}.md"
elif [ -f ".claude/PRPs/issues/issue-{number}.md" ]; then
  artifact_path=".claude/PRPs/issues/issue-{number}.md"
  echo "Legacy investigation artifact found; run the PRP home-store migration."
else
  echo "Artifact not found at $PRP_DIR/issues/issue-{number}.md"
fi
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
❌ Artifact not found at `$PRP_DIR/issues/issue-{number}.md` (or the legacy `.claude/PRPs/issues/issue-{number}.md`).

Run `/prp-issue investigate {number}` first to create the implementation plan. If only the legacy path exists, run the PRP home-store migration first.
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

`{expanded absolute path to $PRP_DIR/issues/issue-{number}.md}`

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

## Phase 8: REVIEW - Review the PR, then act on it

The review agents read the diff; you read what they report. Dispatch the review first, then spend
the rest of this phase acting on its findings.

### 8.1 Run the review

Skill tool, `skill: "prp-core:prp-review"`, `args: "{pr-number}"`.

That is the whole of this step. It dispatches the reviewers, writes
`$PRP_DIR/reviews/pr-{pr-number}-review.md`, and posts the summary to the PR.

- The review skill always runs `prp-core:code-reviewer` and `prp-core:seam-analyzer`. Add a named
  specialist scope only when the issue or user explicitly calls for it.
- **The review comment on the PR is written by the review skill.** Your own comment comes later, in
  8.3, and it records what you applied and what you declined.

### 8.2 Act on the findings

A review nobody acts on is a comment. Work the report:

- **Critical and Important — fix them**, unless the finding is wrong. If it is wrong, say why in
  8.3; do not fix it silently and do not ignore it silently.
- **Suggestions — judge each one, and expect to decline some.** Apply what makes the change simpler
  or more correct. Decline anything that adds a capability nobody asked for (YAGNI), generalizes
  for a second caller that does not exist, adds a layer, an option, or a config knob to a thing
  with one use, or trades a plain implementation for a clever one.
- **Out of scope is a real answer.** A finding about code this PR did not touch belongs in an
  issue, not in this diff. File it or name it; do not widen the PR to swallow it.

When the finding is genuine but the proposed remedy is over-built, fix the finding the small way
rather than declining it.

After applying anything: **re-run Phase 6's validation**, then commit and push. A review fix that
breaks the gate is worse than the finding it addressed.

```bash
git add -A
git commit -m "fix(scope): address review findings on #{number}"
git push
```

### 8.3 Say what you did with it

One short comment on the PR, so the declines are visible rather than silent:

```bash
gh pr comment {pr-number} --body "$(cat <<'EOF'
### Review findings — applied

- `{file}:{line}` — {what changed}

### Declined

- {finding} — {why: YAGNI / out of scope / disagreed, and on what grounds}

Validation re-run after the changes: {result}
EOF
)"
```

If nothing was declined, drop that section rather than writing "none" — and if nothing needed
fixing at all, say that in one line instead of posting the template.

**PHASE_8_CHECKPOINT:**

- [ ] `prp-review` dispatched against the PR; default code and seam review report written and posted by it
- [ ] `$PRP_DIR/reviews/pr-{pr-number}-review.md` exists on disk
- [ ] Critical and Important findings fixed, or explicitly rejected with a reason
- [ ] Suggestions judged individually; over-engineered ones declined
- [ ] Validation re-run and green after any change; commits pushed
- [ ] Applied/declined comment posted

---

## Phase 9: ARCHIVE - Clean Up

### 9.0 Gate: the review left a file

Phase 8 writes a report to a known path. Check for it before archiving anything:

```bash
ls -1 "$PRP_DIR/reviews/pr-{pr-number}-review.md"
```

**Exit 0 — the review ran.** Continue to 9.1.

**Non-zero — Phase 8 did not run.** Go back to Phase 8, run it, act on the findings, and return
here. This is a file check rather than a question you answer from memory, because by this point in
the run the memory is the unreliable part: the PR is open, the diff is green, and the work reads as
finished several phases before it is. Archiving is the last step of a reviewed fix.

### 9.1 Move Artifact to Completed

```bash
mkdir -p "$PRP_DIR/issues/completed"
mv "$PRP_DIR/issues/issue-{number}.md" "$PRP_DIR/issues/completed/"
```

If the artifact was loaded from the legacy fallback, stop and ask the user to migrate it rather than archiving it in place.

### 9.2 Confirm Archive

Do **not** stage, commit, or push the archive; it is stored outside the repository.

**PHASE_9_CHECKPOINT:**

- [ ] Review report confirmed present on disk before archiving
- [ ] Artifact moved to the PRP store's completed folder

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

### Review

{What the review found, what was applied, what was declined and why}

### Artifact

📄 Archived to `{expanded absolute path to $PRP_DIR/issues/completed/issue-{number}.md}`

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
- **REVIEWED_BY_AGENTS**: `prp-review` run against the PR with its default code and seam agents; `$PRP_DIR/reviews/pr-{pr-number}-review.md` exists and its summary is posted
- **FINDINGS_ACTIONED**: Every Critical/Important fixed or rejected with a reason; declines stated on the PR
- **ARTIFACT_ARCHIVED**: Moved to completed folder
- **AUDIT_TRAIL**: GitHub comment and PRP-store artifact history
