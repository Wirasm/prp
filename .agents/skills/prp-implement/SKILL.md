---
name: prp-implement
description: Implements and validates existing PRP plans. Always use when executing an implementation plan, when the user explicitly asks to build or implement a plan, when another PRP workflow reaches its implementation step, or when the user invokes $prp-implement.
---

> **Arguments:** `$ARGUMENTS` (and `$1`, `$2`, ...) refer to the arguments given when this skill was invoked. Take them from the user's request; if absent, infer them from the conversation.

# Implement Plan

Execute the supplied implementation plan through a validated commit and pull request. Keep implementation, commit, and PR creation in this context; leave review to its own context.

**Plan**: $ARGUMENTS

## 1. Establish context

Resolve the plan path from the arguments or conversation and read the entire file. Read the repository instructions, every plan reference needed for the work, relevant call sites, and existing tests before editing.

Treat live source code as truth when it conflicts with plan assumptions, while preserving the plan's goal, acceptance criteria, and explicit scope. If reality makes the intended outcome ambiguous or materially changes product shape, stop and ask. If implementation would require working around a missing foundational primitive that should exist first, stop and explain the missing primitive, why it belongs earlier, and what it blocks. Otherwise record the necessary deviation and continue.

Use the current feature branch or assigned worktree when one exists. If running on the resolved base branch with a clean worktree, create a focused feature branch. Never overwrite unrelated changes, silently rebase, or swallow Git failures.

## 2. Implement the plan

Execute tasks in dependency order and read each referenced pattern before changing its task. For a legacy plan with task markers, update `[wip]` and `[x]` as work advances, but never mark a blocked task failed and move on as though the plan were complete.

Apply these implementation principles:

- Prefer the simplest solution that solves the actual problem. Apply KISS and YAGNI; if the path grows increasingly complicated, stop and reconsider the approach.
- Reproduce bugs before fixing them whenever reasonably possible. When reproduction is impossible, establish other concrete evidence and record it.
- Existing code is evidence, not proof that its design is correct. Rewrite only when that clearly reduces complexity without widening scope or risk.
- Use the type system to express meaningful invariants. Avoid unsound escape hatches when a practical sound type exists.
- Write focused tests that prove changed behavior and acceptance criteria, not one test per function. For bug fixes, add a regression test that fails before the fix and passes after it when practical. Prefer behavioral contracts over snapshots or implementation-detail assertions. Do not add coverage theater, smoke-test volume, or tests whose only purpose is preserving removed behavior.
- Keep comments and documentation accurate when behavior changes. Comment important intent and constraints, not every line.

Never defer work required by the plan or its acceptance criteria: complete it now or mark the implementation `BLOCKED`. For actionable work discovered outside the agreed scope, avoid widening the implementation; create or link a human-visible GitHub issue before reporting green, and carry that issue into the report and PR description so normal repository triage and `$prp-worklist` can pick it up. If durable tracking cannot be established, stop and ask the user where it belongs; do not bury it in the report or report green. Omit optional ideas that do not merit a commitment.

Record deviations and implementation-only decisions in the implementation report. For a legacy plan that explicitly provides maintained Agent Notes or Amendments sections, keep those current as well. Do not move or archive the plan.

## 3. Validate to green

Run each task's specified validation after the coherent task, then run every applicable command or procedure in the plan's Validation section and verify every Acceptance criterion. For a legacy plan, honor its Validation Commands and Acceptance Criteria. Add or adapt a missing check only when repository evidence shows the plan's gate is incomplete.

On failure, fix the cause and rerun the affected check before continuing. Do not trust the first passing suite blindly: inspect suspicious or weak tests and verify the behavior they claim to cover. Never report completion with a known failing required check.

## 4. Write the implementation report

Resolve the canonical project store:

```bash
# --- PRP store resolver (canonical; keep byte-identical across skills) ---
_gd="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"
case "$_gd" in */.git) _root="${_gd%/.git}" ;; "") _root="$PWD" ;; *) _root="$_gd" ;; esac
_root="$(cd "$_root" && pwd -P)"
_name="$(basename "$_root" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-*//;s/-*$//')"
PRP_DIR="${PRP_HOME:-$HOME/.prp}/${_name:-project}-$(printf %s "$_root" | git hash-object --stdin | cut -c1-8)"
mkdir -p "$PRP_DIR"; [ -f "$PRP_DIR/project.json" ] || printf '{"path": "%s", "name": "%s"}\n' "$_root" "${_name:-project}" > "$PRP_DIR/project.json"
```

Create `$PRP_DIR/reports/` and write `$PRP_DIR/reports/{plan-name}-report.md`. Before writing it, read `templates/implementation-report.md` and follow that structure exactly.

The report is the durable handoff across context windows. Keep it concise and record only the outcome, validation evidence, deviations or decisions downstream agents need, completion-gate evidence, intended commit scope, and delivery evidence. Preserve the plan-based filename and include branch metadata in the report; downstream skills own discovering it.

If implementation or required validation is blocked, mark the report `BLOCKED`, do not commit or open a PR, and return the concrete blocker.

## 5. Commit, open the PR, and update linked context

When implementation is green, invoke `$prp-commit` for only the work completed from this plan. Record the resulting commit SHA in the report and in a legacy plan's append-only Lifecycle section when present.

Then invoke `$prp-pr`, passing the explicit `--base` argument when supplied and any tracked follow-up issue links as context for the PR description. Let that skill resolve the base otherwise. Record the PR URL, base, and head in the report.

If the plan has non-empty `Source PRD` and `PRD Phase` metadata, invoke `$prp-prd-update implemented` with the PRD path, phase number, plan path, report path, and PR URL. Do not edit the PRD directly. If the plan is not based on a PRD, skip this step.

If committing, pushing, PR creation, or the required PRD update fails, leave the recoverable state intact, mark the report `BLOCKED`, and return the concrete failure.

## 6. Verify and hand off

Re-read the branch diff, updated plan, and report. Confirm the intended implementation is complete, unrelated work remains untouched, every reported validation result is factual, the commit contains the intended scope, the PR targets the correct base, and the report exists at the stated absolute path.

Return the implemented outcome, validation summary, deviations or blocker and recovery action, commit, PR URL, tracked follow-up issues, conditional PRD update, and absolute report path. Do not review, merge, move, or archive the plan.

When every required validation and acceptance criterion passes and every required delivery step succeeds, end the response with exactly `VALIDATION: GREEN`. Otherwise end with `VALIDATION: FAILED` followed by the concrete blocker or failing output.

## Resources

- `templates/implementation-report.md` — mandatory format for the cross-context implementation handoff.
