---
name: prp-pr
description: Create a PR from current branch with unpushed commits. Use when the user wants to open or create a pull request, push and PR a branch, or invokes $prp-pr.
---

> **Arguments:** `$ARGUMENTS` (and `$1`, `$2`, ...) refer to the arguments given when this skill was invoked. Take them from the user's request; if absent, infer them from the conversation.

# Create Pull Request

**Base branch override**: $ARGUMENTS

---

## Your Mission

Create a well-formatted pull request from the current branch, using repository PR templates if available, with a clear summary of changes.

**Golden Rule**: PRs should tell reviewers what changed and why. Use existing templates when available.

---

## Phase 0: DETECT - Base Branch

### 0.1 Detect Base Branch

Determine the base branch for PR target and diff comparison:

1. **Check arguments**: If `$ARGUMENTS` contains a branch name or `--base <branch>`, use that value
2. **Auto-detect from remote**:
   ```bash
   git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'
   ```
3. **Fallback if detection fails**:
   ```bash
   git remote show origin 2>/dev/null | grep 'HEAD branch' | awk '{print $NF}'
   ```
4. **Last resort**: `main`

**Store as `{base-branch}`** — use this value for ALL comparisons, diff commands, and PR creation. Never hardcode `main` or `master`.

---

## Phase 1: VALIDATE - Check Prerequisites

### 1.1 Verify Git State

```bash
# Current branch (must not be {base-branch})
git branch --show-current

# Check for uncommitted changes
git status --short

# Verify we have commits to PR
git log origin/{base-branch}..HEAD --oneline
```

**Decision Tree:**

| State | Action |
|-------|--------|
| On {base-branch} | STOP: "Cannot create PR from {base-branch}. Create a feature branch first." |
| Uncommitted changes | WARN: "You have uncommitted changes. Commit or stash before creating PR." |
| No commits ahead | STOP: "No commits to create PR from. Branch is up to date with {base-branch}." |
| Has commits, clean | PROCEED |

### 1.2 Check for Existing PR

```bash
gh pr list --head $(git branch --show-current) --json number,url
```

**If PR exists:**
```
PR already exists for this branch: {url}
Use `gh pr view` to see details or `gh pr edit` to modify.
```

**PHASE_1_CHECKPOINT:**
- [ ] Not on {base-branch}
- [ ] Working directory is clean (or user acknowledged)
- [ ] Has commits ahead of base branch
- [ ] No existing PR for this branch

---

## Phase 2: DISCOVER - Gather Context

### 2.1 Check for PR Template

```bash
# Check common template locations
ls -la .github/PULL_REQUEST_TEMPLATE.md 2>/dev/null
ls -la .github/pull_request_template.md 2>/dev/null
ls -la .github/PULL_REQUEST_TEMPLATE/ 2>/dev/null
ls -la docs/pull_request_template.md 2>/dev/null
```

**If template found:**
- Read the template
- Use it as the PR body structure
- Fill in sections based on commits and changes

**If no template:**
- Use default format (see Phase 4)

### 2.2 Analyze Commits

```bash
# Get commit messages for PR body
git log origin/{base-branch}..HEAD --pretty=format:"- %s"

# Get detailed commit info
git log origin/{base-branch}..HEAD --pretty=format:"%h %s%n%b" --no-merges
```

### 2.3 Analyze Changed Files

```bash
# Files changed
git diff --stat origin/{base-branch}..HEAD

# Get list of changed files
git diff --name-only origin/{base-branch}..HEAD
```

### 2.4 Determine PR Title

**From commits, derive title:**
- If single commit: Use commit message as title
- If multiple commits: Summarize the change in imperative mood
- Format: `{type}: {description}` (e.g., "feat: Add user authentication")

**Common prefixes:**
| Prefix | Usage |
|--------|-------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `refactor:` | Code restructuring |
| `docs:` | Documentation |
| `test:` | Adding tests |
| `chore:` | Maintenance |

**PHASE_2_CHECKPOINT:**
- [ ] PR template located (or confirmed none exists)
- [ ] Commit messages extracted
- [ ] Changed files listed
- [ ] PR title determined

---

## Phase 3: PUSH - Ensure Branch is Remote

### 3.1 Push to Origin

```bash
# Push with upstream tracking
git push -u origin HEAD
```

**If push fails:**
- Check for remote branch conflicts
- May need `--force-with-lease` if rebased (warn user first)

**PHASE_3_CHECKPOINT:**
- [ ] Branch pushed to origin
- [ ] Upstream tracking set

---

## Phase 4: CREATE - Build and Submit PR

### 4.1 If Template Exists

Read the template and fill in each section based on:
- Commit messages
- Changed files
- Any linked issues (look for `#123` or `Fixes #123` in commits)

### 4.2 If No Template - Use Default Format

```bash
gh pr create \
  --title "{title}" \
  --base "{base-branch}" \
  --body "$(cat <<'EOF'
## Summary

{1-2 sentence description of what this PR accomplishes}

## Changes

{List of commit summaries}
- {commit 1}
- {commit 2}

## Files Changed

{Count} files changed

<details>
<summary>File list</summary>

{list of changed files}

</details>

## Testing

- [ ] Type check passes
- [ ] Tests pass
- [ ] Manually verified

## Related Issues

{Any linked issues from commit messages, or "None"}
EOF
)"
```

### 4.3 Extract Issue References

From commit messages, find patterns like:
- `Fixes #123`
- `Closes #123`
- `Relates to #123`
- `#123`

Include these in the PR body under "Related Issues".

**PHASE_4_CHECKPOINT:**
- [ ] PR body generated (from template or default)
- [ ] Title is clear and follows convention
- [ ] Related issues linked

---

## Phase 5: VERIFY - Confirm Creation

### 5.1 Get PR Details

```bash
# Get the created PR info
gh pr view --json number,url,title,state
```

### 5.2 Verify PR is Ready

```bash
# Check PR status
gh pr checks
```

**PHASE_5_CHECKPOINT:**
- [ ] PR created successfully
- [ ] PR URL retrieved

---

## Phase 6: OUTPUT - Report to User

```markdown
## Pull Request Created

**PR**: #{number}
**URL**: {url}
**Title**: {title}
**Base**: {base-branch} <- {current-branch}

### Summary

{Brief description of what the PR contains}

### Changes

- {N} commits
- {M} files changed

### Files

{List of changed files}

### Checks

{Status of any CI checks, or "Pending"}

### Next Steps

- Wait for CI checks to pass
- Request review if needed: `gh pr edit --add-reviewer @username`
- View PR: `gh pr view --web`
```

---

## Handling Edge Cases

### Branch has diverged from {base-branch}

```bash
# Suggest rebasing first
git fetch origin
git rebase origin/{base-branch}
# Then push with lease
git push --force-with-lease
```

### PR template has required sections

- Parse template for required sections (often marked with `<!-- required -->`)
- Ensure all required sections are filled
- Warn if any appear incomplete

### Multiple PR templates exist

```bash
# If .github/PULL_REQUEST_TEMPLATE/ directory exists
ls .github/PULL_REQUEST_TEMPLATE/
```

- If multiple templates, use the default or ask user which to use

### Draft PR requested

```bash
gh pr create --draft --title "{title}" --body "{body}"
```

---

## Success Criteria

- **BRANCH_PUSHED**: Current branch exists on origin
- **PR_CREATED**: PR successfully created via gh
- **TEMPLATE_USED**: If template exists, it was used
- **ISSUES_LINKED**: Any referenced issues are linked
- **URL_RETURNED**: User has the PR URL to share/review
