---
name: prp-implement
description: Implements and validates existing PRP plans and corrects reviewed or failing-CI pull requests. Always use when executing an implementation plan, implementing an issue that already has a local or published plan, correcting a PR from a PRP review report or CI failure, when another PRP workflow reaches its implementation or correction step, or when the user invokes the prp-implement skill.
---

> **Kild lane:** you are running inside a kild room, in a workspace (worktree + branch) the kild engine assigned. The driver owns isolation and publishing — SKIP any step below that creates or switches branches or worktrees, pulls or rebases the base branch, pushes, opens PRs, or moves/archives plan artifacts, and never run `gh pr checkout`. Your job ends at implement → validate → commit in the current workspace, reporting evidence. Where a step spawns subagents, do that analysis inline — or ask the room's orchestrator to invite a helper agent.

> **Arguments:** `$ARGUMENTS` (and `$1`, `$2`, ...) refer to the arguments given when this skill was invoked. Take them from the user's request; if absent, infer them from the conversation.

# Implement Plan

Execute the supplied implementation plan through a validated commit and pull request, or apply review findings to that pull request. Keep implementation, commit, and PR delivery in this context; leave review judgment to its own context.

**Input**: $ARGUMENTS

## Mode

- A plan path starts the initial implementation.
- `review` plus a review report, PR, or finding decisions starts a correction pass. Resolve and read the original plan, implementation report, live PR diff and comments, complete canonical review report, and any explicit finding dispositions before editing. Human dispositions are binding when supplied. Otherwise Critical or Important findings require correction or an evidence-backed disagreement; suggestions remain optional.
- `ci` plus a PR and failing-check evidence starts a correction pass. Resolve the original plan, implementation report, live PR diff, complete check status and logs, and reproduce the failure before editing. Correct only PR-caused failures; preserve evidence when the failure is external or pre-existing.

Resume the original implementation context for corrections when it is available. In a fresh context, reconstruct the complete contract from those durable artifacts rather than from an abbreviated findings summary.

Resolve the canonical project store before locating artifacts:

```bash
# --- PRP store resolver (canonical; keep byte-identical across skills) ---
_gd="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"
case "$_gd" in */.git) _root="${_gd%/.git}" ;; "") _root="$PWD" ;; *) _root="$_gd" ;; esac
_root="$(cd "$_root" && pwd -P)"
_name="$(basename "$_root" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-*//;s/-*$//')"
PRP_DIR="${PRP_HOME:-$HOME/.prp}/${_name:-project}-$(printf %s "$_root" | git hash-object --stdin | cut -c1-8)"
mkdir -p "$PRP_DIR"; [ -f "$PRP_DIR/project.json" ] || printf '{"path": "%s", "name": "%s"}\n' "$_root" "${_name:-project}" > "$PRP_DIR/project.json"
```

## 1. Establish context

Resolve the plan path from the arguments, linked implementation report, or conversation and read the entire file. When the input is an issue reference rather than a path, normalize number and URL forms to the same tracker item, search `$PRP_DIR/plans/` for matching `Source Issue` metadata, and select the single current plan. If several match, present the newest viable candidates and ask; never guess. If no local plan exists, retrieve the latest complete issue comment marked `<!-- prp-plan-id: ... -->`, persist that published plan under `$PRP_DIR/plans/`, and use it. Never substitute the issue body for a missing plan.

For an issue-derived plan, read comments added after `Plan Publication` before editing. If they correct or materially change the implementation contract, stop and invoke `the prp-plan skill` to revise and republish the plan before implementation; do not implement a knowingly stale plan.

If `Source Issue` is non-empty but `Plan Publication` is empty or cannot be verified on that issue, invoke `the prp-plan skill publish <absolute plan path>`, re-read the plan, and stop if publication remains unverified. Apply this gate whether the input was the issue or the plan path.

Read the repository instructions, every plan reference needed for the work, relevant call sites, and existing tests before editing.

Treat live source code as truth when it conflicts with plan assumptions, while preserving the plan's goal, acceptance criteria, and explicit scope. If reality makes the intended outcome ambiguous or materially changes product shape, stop and ask. If implementation would require working around a missing foundational primitive that should exist first, stop and explain the missing primitive, why it belongs earlier, and what it blocks. Otherwise record the necessary deviation and continue.

Use the current feature branch or assigned worktree when one exists. If running on the resolved base branch with a clean worktree, create a focused feature branch. Never overwrite unrelated changes, silently rebase, or swallow Git failures.

## 2. Implement the plan

For initial implementation, execute tasks in dependency order and read each referenced pattern before changing its task. For a correction pass, change only what the blocking findings, failing checks, or explicit dispositions require and preserve the plan's outcome and invariant. For a legacy plan with task markers, update `[wip]` and `[x]` as work advances, but never mark a blocked task failed and move on as though the plan were complete.

Apply these implementation principles:

- Prefer the simplest solution that solves the actual problem. Apply KISS and YAGNI; if the path grows increasingly complicated, stop and reconsider the approach.
- Reproduce bugs before fixing them whenever reasonably possible. When reproduction is impossible, establish other concrete evidence and record it.
- Existing code is evidence, not proof that its design is correct. Rewrite only when that clearly reduces complexity without widening scope or risk.
- Use the type system to express meaningful invariants. Avoid unsound escape hatches when a practical sound type exists.
- Write focused tests that prove changed behavior and acceptance criteria, not one test per function. For bug fixes, add a regression test that fails before the fix and passes after it when practical. Prefer behavioral contracts over snapshots or implementation-detail assertions. Do not add coverage theater, smoke-test volume, or tests whose only purpose is preserving removed behavior.
- Keep comments and documentation accurate when behavior changes. Comment important intent and constraints, not every line.

Never defer work required by the plan or its acceptance criteria: complete it now or mark the implementation `BLOCKED`. For actionable work discovered outside the agreed scope, avoid widening the implementation; create or link a human-visible GitHub issue before reporting green, and carry that issue into the report and PR description so normal repository triage and `the prp-worklist skill` can pick it up. If durable tracking cannot be established, stop and ask the user where it belongs; do not bury it in the report or report green. Omit optional ideas that do not merit a commitment.

Record deviations and implementation-only decisions in the implementation report. For a legacy plan that explicitly provides maintained Agent Notes or Amendments sections, keep those current as well. Do not move or archive the plan.

## 3. Validate to green

Run each task's specified validation after the coherent task, then run every applicable command or procedure in the plan's Validation section and verify every Acceptance criterion. A correction pass also reruns the focused check for each corrected finding or CI failure. For a legacy plan, honor its Validation Commands and Acceptance Criteria. Add or adapt a missing check only when repository evidence shows the plan's gate is incomplete.

For an evidence-backed disagreement that requires no repository change, run the smallest decisive check that proves the finding invalid and record its output. Do not manufacture a code or documentation edit merely to create a correction commit.

On failure, fix the cause and rerun the affected check before continuing. Do not trust the first passing suite blindly: inspect suspicious or weak tests and verify the behavior they claim to cover. Never report completion with a known failing required check.

## 4. Write the implementation report

Create `$PRP_DIR/reports/` and write `$PRP_DIR/reports/{plan-name}-report.md`. Before writing it, read `templates/implementation-report.md` and follow that structure exactly. A correction pass updates this report to the current delivered truth, including review or CI decisions and new validation and commit evidence; it does not create a parallel correction artifact.

The report is the durable handoff across context windows. Keep it concise and record only the outcome, validation evidence, deviations or decisions downstream agents need, completion-gate evidence, intended commit scope, and delivery evidence. Preserve the plan-based filename and include branch metadata in the report; downstream skills own discovering it.

If implementation or required validation is blocked, mark the report `BLOCKED`, do not commit or open a PR, and return the concrete blocker.

## 5. Commit, open the PR, and update linked context

When initial implementation is green, or a correction changed repository files, invoke `the prp-commit skill` for only the work completed from this plan or correction pass. Record the resulting commit SHA in the report and in a legacy plan's append-only Lifecycle section when present.

For initial implementation, invoke `the prp-pr skill`, passing the explicit `--base` argument when supplied, the plan's source issue and verified `Plan Publication` URL when present, and any tracked follow-up issue links as context for the PR description. Let that skill resolve the base otherwise. For a correction pass with repository changes, push the new commit without force and verify that the existing PR now contains it. For an evidence-only disagreement, skip commit and push, verify the PR head SHA is unchanged, and record that SHA with the decisive evidence. Record the PR URL, base, head, and all delivery commits in the report.

If the plan has non-empty `Source PRD` and `PRD Phase` metadata, invoke `the prp-prd-update skill implemented` with the PRD path, phase number, plan path, report path, and PR URL. Do not edit the PRD directly. If the plan is not based on a PRD, skip this step.

If committing, pushing, PR creation, or the required PRD update fails, leave the recoverable state intact, mark the report `BLOCKED`, and return the concrete failure.

## 6. Verify and hand off

Re-read the branch diff, updated plan, report, and the correction input—the review report or CI evidence. Confirm the intended implementation or required corrections are complete, unrelated work remains untouched, every reported validation result is factual, the commit contains the intended scope, the PR targets the correct base, and the report exists at the stated absolute path.

Return the implemented outcome, resolved absolute plan path, validation summary, deviations or blocker and recovery action, commit, PR URL, tracked follow-up issues, conditional PRD update, and absolute report path. Do not review, merge, move, or archive the plan.

When every required validation and acceptance criterion passes and every required delivery step succeeds, end the response with exactly `VALIDATION: GREEN`. Otherwise end with `VALIDATION: FAILED` followed by the concrete blocker or failing output.

## Resources

- `templates/implementation-report.md` — mandatory format for the cross-context implementation handoff.
