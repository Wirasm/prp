---
name: prp-deliver
description: Delivers work from an issue, PRD, document, plan, or prompt through planning, implementation, pull request, and published review. Always use when the user asks to take work to a reviewed PR, implement or ship an issue end to end, go from plan to PR, continue after a PRP review, or when another PRP workflow reaches full delivery. Use /prp-plan for plan-only work, /prp-review for review-only work, and /prp-loop for detached autonomous execution.
argument-hint: "<issue|PRD|document|plan|description|reviewed PR> [--base <branch>] [review scopes]"
---

# Deliver to a Reviewed PR

Own one outcome from its source input to a reviewed GitHub pull request. Compose the specialist PRP skills; do not reproduce their planning, implementation, commit, PR, or review instructions here.

**Input**: $ARGUMENTS (if absent, use the conversation).

## 1. Resolve the entry point

Accept an issue or tracker URL, PRD, document, existing `.plan.md`, free-form request, or conversation context.

- Existing plan: read its source metadata. If it is issue-derived and lacks a verified `Plan Publication`, invoke `/prp-plan publish <path>` before using it.
- Issue reference with an already published plan: let `/prp-implement` resolve the plan by source metadata when the user asks to continue that work; do not make them remember its filename.
- Existing PR with a published `prp-review` report and finding decisions: resume at the findings gate. Resolve its plan and implementation report from the PR links and project store; do not plan or implement the original scope again.
- Every other input: invoke `/prp-plan` with the complete input. Let the planner retrieve tracker context, investigate broken behavior, research, spike, or hold a design gate as needed.
- Review-only request or an existing contributor PR: use `/prp-review` instead and stop.

Do not translate an issue into a second investigation artifact. The plan is the implementation contract.

Require the absolute plan path before continuing. For every issue-derived plan—regardless of whether the invocation began with the issue or a plan path—also require the verified published-plan URL; stop at the planner's publication blocker rather than beginning an implementation whose shared contract is missing.

## 2. Implement and open the PR

Invoke `/prp-implement` with the absolute plan path—or the source issue when resuming a published plan—and any explicit base. Its context owns implementation, validation, commit, PR creation, linked PRD updates, and the implementation report.

Stop on `VALIDATION: FAILED`. Do not review incomplete implementation or bypass a product, primitive, validation, delivery, or tracking blocker.

## 3. Review in an independent context

Invoke `/prp-review` against the verified PR in a separate review context. Pass through any review scopes the user requested. The review skill is the only path for judging the PR and the only owner of the review report.

Require all three review outputs:

- the canonical `$PRP_DIR/reviews/pr-{number}-review.md` report;
- the complete report published on GitHub as a PR comment by default, or as a formal request-changes review when explicitly requested;
- the verified GitHub publication URL.

Never replace the report with a private verdict, abbreviated finding list, or composition-specific review artifact.

## 4. Hold the findings gate

Return the published report URL and pause for the user to decide what to address. Do not silently convert reviewer advice into implementation scope.

An orchestrator may cross this gate only when an explicit standing decision covers the findings. Otherwise it presents the report and recommendation to the user, records the decision, and resumes this same delivery workstream.

`READY TO MERGE` completes this skill. `REVIEW INCOMPLETE` is a blocker until the missing validation or evidence is resolved. `NEEDS FIXES` continues only after the user or an applicable standing decision dispositions the findings.

## 5. Feed decisions back into implementation

Return the absolute plan path, implementation report, live PR, complete review report, and the user's finding dispositions to the implementation owner.

Resume the original implementation context when it remains available. It owns the code and retains the reasoning that produced it. If that context cannot be resumed, start a fresh `/prp-implement` review-correction run with every artifact above; never reconstruct the task from one-line findings.

The implementation owner addresses the accepted findings, validates, commits only the correction scope, pushes the existing PR branch, and updates the implementation report. A declined blocking finding needs concrete evidence, not preference.

After any correction or evidence-backed disagreement, run `/prp-review` again in a fresh review context and publish the new complete report. Repeat the findings gate until the verdict is `READY TO MERGE` or a concrete blocker requires the user.

## 6. Report the delivered outcome

Return the outcome, plan path, implementation report path, PR URL, latest review verdict, latest review report path, GitHub publication URL, validation summary, and any concrete blocker. Do not merge the PR or mark a linked PRD phase complete; those occur only after a separately verified merge.
