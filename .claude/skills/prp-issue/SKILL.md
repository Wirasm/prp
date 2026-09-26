---
name: prp-issue
description: Autonomously owns one workstream from an issue, PRD, document, existing plan, or free-form request through planning, implementation, pull request, independent review, corrections, and green CI. Always use when the user asks to implement or ship work end to end, take an issue or idea to a reviewed PR, run plan to PR, invokes /prp-issue, or when prp-orchestrate needs an end-to-end delivery engine.
argument-hint: "<issue|PRD|document|plan|description|reviewed PR> [--base <branch>] [review scopes]"
---

# Deliver One Workstream

Own planning through PR and every correction in this context. Preserve accumulated reasoning across that implementation lifecycle; use fresh contexts only where independence is the feature—review.

**Input**: $ARGUMENTS (if absent, use the conversation).

## Contract

- Continue autonomously through plan, implementation, PR, review, correction, re-review, and CI.
- Compose `/prp-plan`, `/prp-implement`, and `/prp-review`; do not reproduce their craft.
- Keep the plan, implementation report, PR, review report, publication URL, validation, and CI as the workstream's proof. Never reduce a handoff to a private summary.
- Stop only for a product decision, missing prerequisite primitive, inaccessible dependency, permission boundary, or repeated no-progress failure that cannot be resolved in this context.
- Do not merge. The caller or outer orchestrator owns that gate.

## 1. Resolve and plan in this context

Accept an issue or tracker URL, PRD, document, existing `.plan.md`, free-form request, conversation context, or reviewed PR.

- Review-only request or contributor PR: use `/prp-review` and stop.
- Existing plan: use it; publish it first with `/prp-plan publish <path>` when issue-derived publication is missing.
- Issue with a published plan: let `/prp-implement` resolve and persist its absolute path from source metadata.
- Existing reviewed PR: resolve its plan and implementation report, then resume correction or verification without repeating completed work.
- Every other input: invoke `/prp-plan` now in this context. Keep its reasoning available for implementation.

For a non-trivial change, run `prp-core:code-simplifier` early, on the plan before implementing it and again on the first working implementation, and fold what it finds into this loop. It catches an overcomplicated direction while it is still cheap to change; a late review gate cannot.

Require the absolute plan path and, for issue-derived plans, the verified publication URL before review.

## 2. Implement through PR in this context

Invoke `/prp-implement` with the plan path—or source issue when resolving a published plan—and any explicit base. Keep ownership in this context through validation, scoped commit, PR creation, linked PRD updates, and the implementation report.

Do not start review without `VALIDATION: GREEN`, the absolute plan and report paths, and a live PR.

## 3. Review in a fresh context

Scale review to risk. A change to prose only (documentation, comments, or configuration wording) skips
review: CI or the repository's local gate is its check. A documented snippet that runs is code, not prose.
Everything else is reviewed, and only through `/prp-review`, which picks reviewers by risk and gives them
a detached checkout. Never point a reviewer at your own working tree.

Start a fresh agent with this prompt:

> Invoke `/prp-review` on `<PR URL or number>` with scopes `<requested scopes, if any>`. Applicable caller decisions and scope constraints, verbatim: `<decisions or "None">`. Read the linked plan and implementation report, publish the complete review to GitHub, and return the verdict, canonical review-report path, verified publication URL, and any blocker. Do not modify the PR.

Require the complete canonical review report and verified GitHub publication.
Wait until all selected review agents have finished and the review coordinator has produced the complete canonical report before addressing any finding; never start correction from partial reviewer messages.

## 4. Disposition findings and re-review

Read the complete report in this implementation context and disposition every finding by judgment, not by applying reported findings blindly: reviewers can be wrong or just have taste. Fix what matters by the review's severity definition now, in this loop, including adjacent findings that touch or affect what this change works on; code is cheap, and fixing in the same loop is cheaper than logging and rerunning. Give a real finding that is completely unrelated to the change `TRACKED FOLLOW-UP` with a verified issue link. A taste-level finding that fits the project's direction and engineering docs is fixed now like any other. Use `DECLINED` with the reason for taste that contradicts those docs or has no basis in them, a wrong finding, speculative defense-in-depth, or overengineering, and do not create an issue; use `NOT A FINDING` with decisive evidence when it is false or already satisfied. Never leave a bare deferred state.

Batch every accepted correction and evidence-backed disposition into one coherent pass, then invoke `/prp-implement` in review-correction mode in this same context. What goes is the extra round to confirm routine fixes, not the fixes. Start a fresh `/prp-review --verify-corrections` agent only when the pass fixed a blocking finding, when a fix is itself risky (it changes behavior, or touches a wire format, persisted state, isolation, or security), or when a disposition is disputed. Give it the previous reviewed head, current PR head, complete canonical report, and dispositions, so it verifies those fixes' diff. Every other fix needs no review round: post one PR comment giving each finding's disposition (fixed at `<sha>`, declined with the reason, or tracked with its issue), and a `READY TO MERGE` verdict stands for the new head. Do not wait for or check CI between rounds; CI clears once, at the end of the workstream, on the final head.

Repeat correction and focused verification only for an unresolved prior blocker, a disproven disposition, or a defect caused by the correction. Return to a full review only when the correction materially changed the PR's outcome, architecture, or scope. Continue until the independent verdict is `READY TO MERGE` and every finding has a terminal disposition. Resolve `REVIEW INCOMPLETE` by obtaining its missing validation or evidence; stop only when that is genuinely unavailable.

## 5. Require green CI

After `READY TO MERGE`, wait for every required CI check. A head that only brought the base in, with the PR's own diff unchanged, keeps the verdict; CI on that head is its proof. A pending check is not green. For a PR-caused failure, invoke `/prp-implement` in CI-correction mode with the PR and complete failing-check evidence in this context, then run `/prp-review --verify-corrections` against the changed head. When no required CI exists, rerun the repository's authoritative local gate and record it instead.

## 6. Return proof and follow-ups

Only after review and CI are green, return the outcome, absolute plan and implementation-report paths, PR URL, latest review verdict, review-report path, publication URL, validation, and CI evidence. Then suggest only meaningful remaining non-blocking follow-ups, including already-created tracking issues; do not present required unfinished work as optional follow-up.
