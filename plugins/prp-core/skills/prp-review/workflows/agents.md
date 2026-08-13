# Agent Review Workflow

Review the target PR through specialist agents, then publish one evidence-based summary.

## 1. Resolve the PR and context

Resolve a number, URL, branch, or the current branch's PR with `gh pr view` / `gh pr list`. Read its
title, body, author, state, base, head, files, reviews, comments, and complete diff.

- Stop when the PR is merged. Warn before reviewing a closed PR.
- Review a draft normally, but post a comment rather than approving or requesting changes.
- Check out the PR branch with `gh pr checkout` unless it is already checked out.
- Read repository guidance, the full changed files, and directly relevant tests and precedents.
- Read matching implementation reports, completed plans, or issue artifacts under `$PRP_DIR` when
  they exist. Treat documented deviations as context, not automatic defects.
- If the only matching artifact is under a legacy `.claude/PRPs/` path, stop and tell the user to
  run the PRP home-store migration.

Do not edit files, resolve conflicts, rebase, commit, or push. Review the PR as it exists.

## 2. Run repository validation

Discover authoritative checks from repository guidance, package scripts, task runners, and CI.
Run the applicable type check, lint, tests, build, and any focused validation the changed behavior
requires. Do not invent a generic command merely to fill a category.

Record the exact command, result, and decisive output. A missing or inapplicable check is `not run`,
not a pass. Distinguish a PR-caused failure from an unrelated or pre-existing failure when evidence
allows; otherwise report the uncertainty.

## 3. Select scopes

Always select `code` and `seams`. Add only scopes explicitly named by the user or calling workflow:

| Scope | Agent | Focus |
|---|---|---|
| `code` | `prp-core:code-reviewer` | Correctness, repository rules, high-confidence defects |
| `seams` | `prp-core:seam-analyzer` | Missing types, counterpart drift, bypassed boundaries |
| `tests` | `prp-core:pr-test-analyzer` | Behavioral coverage and valuable regression protection |
| `comments` | `prp-core:comment-analyzer` | Accuracy and long-term value of changed comments |
| `errors` | `prp-core:silent-failure-hunter` | Swallowed failures, fallbacks, and actionable errors |
| `types` | `prp-core:type-design-analyzer` | Invariant expression and enforcement in changed types |
| `docs` | `prp-core:docs-impact-agent` | Stale or missing user and contributor documentation |
| `simplify` | `prp-core:code-simplifier` | Behavior-preserving clarity improvements |

`all` adds all six optional scopes. Explicit `code` or `seams` is redundant but valid. Ignore
`--agents`; it exists only so older callers still receive the new default review.

## 4. Launch reviewers

Dispatch every selected agent in parallel in one message. Wait for all of them before aggregation.
All agents are advisory and must not modify files or post their own PR comments.

When launching each agent via Task tool:

**prp-core:code-reviewer**:
> Review PR #<number> against its actual base for project guideline compliance, bugs, and quality issues. Read the repository guidance and relevant code outside the diff. Report only high-confidence findings with evidence and file:line locations. Do not modify files, commit, or post comments.

**prp-core:seam-analyzer**:
> Analyze PR #<number> for missing types at seams. Leave the diff to inspect direct counterparts of changed payloads, wire formats, persisted or resumed values, IPC/FFI and cross-language boundaries, syntax forms, validators, and synchronized enumerations. Enforce the two-sided evidence bar and documented carve-outs. Do not modify files, commit, or post comments.

**prp-core:pr-test-analyzer**:
> Analyze behavioral test coverage for PR #<number>. Identify only gaps that protect meaningful behavior or prevent realistic regressions. Account for existing integration coverage. Do not modify files, commit, or post comments.

**prp-core:comment-analyzer**:
> Analyze comments changed by PR #<number> for factual accuracy and long-term value. Verify them against actual behavior. Do not modify files, commit, or post comments.

**prp-core:silent-failure-hunter**:
> Hunt for silent failures in PR #<number>, including swallowed errors, unjustified fallbacks, and non-actionable failure handling. Ground findings in reachable behavior. Do not modify files, commit, or post comments.

**prp-core:type-design-analyzer**:
> Analyze new or modified types in PR #<number> for pragmatic invariant expression and enforcement. Recommend added complexity only when it prevents a concrete failure. Do not modify files, commit, or post comments.

**prp-core:docs-impact-agent**:
> Review documentation affected by PR #<number>. Find statements made stale by the change and genuinely necessary user-facing additions. Do not treat steering files as changelogs. Do not modify files, commit, or post comments.

**prp-core:code-simplifier**:
> Identify behavior-preserving simplifications in PR #<number>. Prefer clarity and fewer moving parts; do not optimize for line count or propose speculative abstractions. Do not modify files, commit, or post comments.

## 5. Aggregate without re-reviewing

Read `../templates/review-report.md` before writing. Merge duplicate findings, preserve meaningful
disagreement, and map agent language into the canonical severity categories. Do not invent findings,
raise severity without evidence, or perform another code review during aggregation.

Verdict rules:

- `READY TO MERGE`: no Critical or Important findings and all required validation passed.
- `NEEDS FIXES`: at least one Critical or Important finding, or a PR-caused required validation failure.
- `REVIEW INCOMPLETE`: required validation or decisive evidence could not be obtained.
- Suggestions, including every `simplify` finding, never block by themselves.

Write the report to the expanded absolute path `$PRP_DIR/reviews/pr-{NUMBER}-review.md`.

## 6. Publish and report

Post the report with `gh pr comment` by default. Use `gh pr review --approve` only when `--approve`
was explicitly requested and the verdict is `READY TO MERGE`. Use `gh pr review --request-changes`
when explicitly requested or when the user explicitly asked the skill to submit blocking findings
as a formal review. Never formally approve or request changes on a draft.

Read the PR back to verify the comment or review exists and capture its URL. Return the PR URL,
verdict, finding counts, validation summary, selected scopes, absolute report path, and comment URL.
