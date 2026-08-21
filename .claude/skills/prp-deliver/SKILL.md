---
name: prp-deliver
description: This is an experimental skill. Never use it unless the user explicitly tells you to invoke /prp-deliver.
argument-hint: "<issue|PRD|document|plan|description|reviewed PR> [--base <branch>] [review scopes]"
---

# Deliver to a Reviewed PR

Own one outcome from source input to a published `READY TO MERGE` review and green CI. Act as the sub-orchestrator for this delivery: start and steer specialist agents, preserve their handoff artifacts, and do not implement or review the work in this context.

**Input**: $ARGUMENTS (if absent, use the conversation).

## Ownership contract

- Continue autonomously through plan, implementation, PR, review, correction, re-review, and CI. A published report is observable progress, not a pause point.
- Run stages sequentially in the delivery owner's checkout. Only one implementation or correction agent may mutate it at a time.
- Use a fresh agent for planning, a fresh agent for implementation, and a fresh independent agent for every review. Resume the implementation agent for corrections while it remains available.
- Keep the plan path, implementation report, PR, latest review report, publication URL, and agent handles. Durable artifacts—not recalled summaries—cross context windows.
- Keep a verbatim caller-decisions record of two kinds: constraints that bind the whole delivery, such as scope, base, and product decisions; and dispositions attached to one finding or blocker. A constraint applies to every later stage. A disposition applies only to the finding it names, while that finding is live. Update the record when the caller resolves a blocker, and pass each fresh agent the constraints plus the dispositions its stage acts on, verbatim.
- Carry the burden of proof. Prove completion with green validation, the live PR, the complete published review, its `READY TO MERGE` verdict, and green required CI.
- Stop only when a product decision, missing prerequisite primitive, inaccessible dependency, permission boundary, or repeated no-progress failure cannot be resolved autonomously. Report the exact decision or access needed and a recommendation.
- Do not merge the PR. The caller owns the merge gate.

## 1. Resolve and plan

Accept an issue or tracker URL, PRD, document, existing `.plan.md`, free-form request, conversation context, or reviewed PR.

- Review-only request or contributor PR: use `/prp-review`; this is not a delivery run.
- Existing plan: use it. If it is issue-derived and lacks a verified `Plan Publication`, start a planning agent with `/prp-plan publish <absolute-path>` first.
- Issue whose plan was already published: let `/prp-implement` resolve it from source metadata and require that agent to return the persisted absolute plan path.
- Existing PR with a published PRP review: resolve its plan and implementation report, then enter correction or review without repeating completed stages.
- Otherwise start a fresh agent with this prompt:

> Invoke `/prp-plan` against `<complete input>`. Additional caller context: `<relevant context and explicit base, if any>`. Caller constraints, verbatim: `<constraints or "None">`. Return the absolute plan path, source and publication URLs, and any concrete blocker.

Require an absolute plan path before review and, for issue-derived plans, a verified published-plan URL.

## 2. Implement and open the PR

Start a fresh agent in the same checkout with this prompt:

> Invoke `/prp-implement` on `<absolute plan path or source issue>` with base `<explicit base, if any>`. Caller constraints, verbatim: `<constraints or "None">`. Own implementation through validation, scoped commit, PR creation, linked PRD updates, and the implementation report. Return `VALIDATION: GREEN`, the resolved absolute plan path, absolute report path, and PR URL; otherwise return the concrete blocker.

Do not begin review without `VALIDATION: GREEN`, a live PR, and the implementation report.

## 3. Review independently

Start a fresh agent with this prompt:

> Invoke `/prp-review` on `<PR URL or number>` with scopes `<requested scopes, if any>`. Caller constraints, verbatim: `<constraints or "None">`. Publish the complete review to GitHub. Return the verdict, canonical review-report path, verified publication URL, and any review blocker.

Require the complete canonical review report, its absolute path, its complete GitHub publication, and the verified publication URL.

## 4. Correct and re-review until ready

For `NEEDS FIXES`, `REVIEW INCOMPLETE`, or any `OPEN` finding, send the complete review report—not an abbreviated finding list—to the implementation agent:

> Continue this delivery by invoking `/prp-implement` in review-correction mode for `<PR>`. Read `<plan>`, `<implementation report>`, and the complete review at `<review report>`. Caller constraints and the dispositions for findings in this report, verbatim: `<constraints and dispositions or "None">`. Disposition every finding under the skill's fix-now, follow-up, and decline rules. Restore `VALIDATION: GREEN` and update the implementation report. Commit and push only when repository changes are required; for an evidence-only disposition, prove the PR head is unchanged.

Let the implementation agent disposition the report using its plan and code context. Prefer fixing valid, narrow, low-risk findings now; track only valuable distinct outcomes, and decline speculative or directionally wrong work without creating backlog noise.

If that agent is unavailable, start a fresh correction agent with the same complete artifact bundle. After every correction or disposition, start another fresh review agent with the caller constraints, the complete canonical report, and the dispositions under verification, then update the canonical publication. Repeat until `READY TO MERGE` with every finding terminal, or a genuine blocker survives without new evidence or progress.

## 5. Require green CI

After `READY TO MERGE`, wait for every required CI check. A pending check is not green. Return a PR-caused failure and its complete evidence to the implementation agent and tell it to invoke `/prp-implement` in CI-correction mode, then run a fresh review against the changed head. When the repository has no required CI, rerun its authoritative local validation instead and record that evidence.

## 6. Return the outcome

Return the implemented outcome, absolute plan and implementation-report paths, PR URL, `READY TO MERGE` verdict, latest review-report path, GitHub publication URL, validation summary, and CI results. These are the proof the caller verifies before accepting the workstream. Only then suggest meaningful remaining non-blocking follow-ups. If genuinely blocked, return the same artifact bundle plus the exact blocker and recommended next action.
