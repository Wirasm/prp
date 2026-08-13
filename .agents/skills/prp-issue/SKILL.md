---
name: prp-issue
description: Autonomously owns one workstream from an issue, PRD, document, existing plan, or free-form request through planning, implementation, pull request, independent review, corrections, and green CI. Always use when the user asks to implement or ship work end to end, take an issue or idea to a reviewed PR, run plan to PR, invokes $prp-issue, or when prp-orchestrate needs an end-to-end delivery engine.
---

> **Arguments:** `$ARGUMENTS` (and `$1`, `$2`, ...) refer to the arguments given when this skill was invoked. Take them from the user's request; if absent, infer them from the conversation.

# Deliver One Workstream

Own planning through PR and every correction in this context. Preserve accumulated reasoning across that implementation lifecycle; use fresh contexts only where independence is the feature—review.

**Input**: $ARGUMENTS (if absent, use the conversation).

## Contract

- Continue autonomously through plan, implementation, PR, review, correction, re-review, and CI.
- Compose `$prp-plan`, `$prp-implement`, and `$prp-review`; do not reproduce their craft.
- Keep the plan, implementation report, PR, review report, publication URL, validation, and CI as the workstream's proof. Never reduce a handoff to a private summary.
- Stop only for a product decision, missing prerequisite primitive, inaccessible dependency, permission boundary, or repeated no-progress failure that cannot be resolved in this context.
- Do not merge. The caller or outer orchestrator owns that gate.

## 1. Resolve and plan in this context

Accept an issue or tracker URL, PRD, document, existing `.plan.md`, free-form request, conversation context, or reviewed PR.

- Review-only request or contributor PR: use `$prp-review` and stop.
- Existing plan: use it; publish it first with `$prp-plan publish <path>` when issue-derived publication is missing.
- Issue with a published plan: let `$prp-implement` resolve and persist its absolute path from source metadata.
- Existing reviewed PR: resolve its plan and implementation report, then resume correction or verification without repeating completed work.
- Every other input: invoke `$prp-plan` now in this context. Keep its reasoning available for implementation.

Require the absolute plan path and, for issue-derived plans, the verified publication URL before review.

## 2. Implement through PR in this context

Invoke `$prp-implement` with the plan path—or source issue when resolving a published plan—and any explicit base. Keep ownership in this context through validation, scoped commit, PR creation, linked PRD updates, and the implementation report.

Do not start review without `VALIDATION: GREEN`, the absolute plan and report paths, and a live PR.

## 3. Review in a fresh context

Start a fresh agent with this prompt:

> Invoke `$prp-review` on `<PR URL or number>` with scopes `<requested scopes, if any>`. Applicable caller decisions and scope constraints, verbatim: `<decisions or "None">`. Read the linked plan and implementation report, publish the complete review to GitHub, and return the verdict, canonical review-report path, verified publication URL, and any blocker. Do not modify the PR.

Require the complete canonical review report and verified GitHub publication.

## 4. Disposition findings and re-review

Read the complete report in this implementation context. Fix Critical or Important findings that are correct and material to the requested outcome. Record concrete evidence when a finding is false, already satisfied, conflicts with an explicit decision, or belongs outside the agreed invariant. Treat Suggestions as optional; adopt one only when it clearly improves this delivery without widening scope or risk.

Invoke `$prp-implement` in review-correction mode in this same context. After every correction or evidence-backed disagreement, start a fresh `$prp-review` agent against the current PR head. Repeat until the independent verdict is `READY TO MERGE`. Resolve `REVIEW INCOMPLETE` by obtaining its missing validation or evidence; stop only when that is genuinely unavailable.

## 5. Require green CI

After `READY TO MERGE`, wait for every required CI check. A pending check is not green. For a PR-caused failure, invoke `$prp-implement` in CI-correction mode with the PR and complete failing-check evidence in this context, then run a fresh review against the changed head. When no required CI exists, rerun the repository's authoritative local gate and record it instead.

## 6. Return proof and follow-ups

Only after review and CI are green, return the outcome, absolute plan and implementation-report paths, PR URL, latest review verdict, review-report path, publication URL, validation, and CI evidence. Then suggest only meaningful remaining non-blocking follow-ups, including already-created tracking issues; do not present required unfinished work as optional follow-up.
