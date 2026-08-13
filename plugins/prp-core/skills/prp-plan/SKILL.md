---
name: prp-plan
description: Creates an implementation-ready plan for a feature, bug fix, refactor, or chore from a PRD, issue, document, or description using codebase evidence, first-principles reasoning, and conditional root-cause analysis, research, or spikes. Publishes issue-derived plans back to their source issue. Use when the user asks to "plan this feature", "plan this bug fix", "plan issue X", "create an implementation plan", "turn this PRD into a plan", investigate how a change should be built, link related plans, or invokes /prp-plan.
argument-hint: <feature description | path/to/prd.md> | update-references <plan-path> <related-plan-path> [back|forward]
---

# PRP Plan

Produce a plan a human can scan and an implementation agent can execute without rediscovering the design. Identify the invariant, find the existing primitives, and choose the smallest solution supported by evidence.

Plan only. Do not implement, commit, or open a PR. A spike is allowed only to settle an architectural hinge; its code remains throwaway under the `prp-spike` contract.

**Input**: $ARGUMENTS (if absent, use the conversation).

## Mode

- A request to link two existing plans routes to `workflows/update-references.md` and stops.
- A bug report, stack trace, regression, error, or unexplained current behavior adds root-cause analysis before solution design.
- Everything else creates an implementation plan.

## 1. Resolve the request

Accept a PRD path, issue reference or URL, another document, free-form text, or conversation context.

For a PRD:

1. Read it and select the first pending phase whose dependencies are complete.
2. Preserve its problem, user, hypothesis, scope, and success signal.
3. Note other independently actionable phases, but plan only the selected phase.
4. Tell the user which phase was selected.

For an issue from GitHub, Jira, Linear, or another tracker:

1. Retrieve the issue through whatever access is already configured in the environment. The skill does not prescribe or configure a tracker client.
2. Treat the body as the starting point, not the complete brief. Read the relevant comment history—including earlier published PRP plans and corrections after them—and follow linked issues, parent/child or blocking relationships, duplicates, PRs, specifications, and attachments that can change scope, intent, constraints, or current decisions.
3. Reconcile that context: distinguish current decisions from superseded discussion, note unresolved disagreements, and stop following links once additional material no longer affects the plan. Curate; do not dump the tracker graph.
4. Preserve the source issue in the plan while separating its required outcome from any suggested implementation.
5. If the issue, comments, or decision-relevant links cannot be retrieved, state what context is missing and ask the user to provide it or configure access. Never infer missing tracker content.

For every input, establish:

- the problem and user outcome;
- the affected user, operator, or system;
- the observable invariant that must hold;
- the success signal that would show the outcome improved after delivery;
- constraints that are genuinely fixed;
- assumptions inherited from the request;
- whether a proposed implementation is required or merely suggested.

Do not invent personas, business value, or vanity metrics. If the affected user, problem, desired outcome, or meaningful success signal is materially uncertain, stop and recommend clarifying the product intent before architecture turns assumptions into code. Ask the user only when ambiguity changes the product contract or would produce materially different plans.

## 2. Gather codebase evidence

Read repository guidance and discover the actual project structure. Do not assume `src/`, a framework, or a validation stack.

For a non-trivial code change, read `references/agent-prompts.md`, then launch these agents in parallel:

- `prp-core:codebase-explorer` to locate relevant files, analogous behavior, tests, configuration, and existing primitives.
- `prp-core:codebase-analyst` to trace the current control flow, data flow, state changes, contracts, and observable behavior.
- For broken current behavior, `prp-core:root-cause-analyzer` to reproduce the symptom, falsify competing explanations, and prove the causal chain and smallest fix boundary.

For a small documentation, configuration, or narrowly localized change, use only the agent or direct inspection needed to remove uncertainty. The planner owns synthesis and must inspect the decisive files itself.

Collect only relevant evidence:

- precise `file:line` references;
- existing primitives and extension points;
- the closest useful precedent, including meaningful variations;
- authoritative project validation commands;
- conventions the change should preserve;
- awkward seams or missing primitives the requested feature would otherwise work around.

Do not preserve a known poor local convention merely because it exists. Fit the architecture while applying repository and global quality guidance.

## 3. Establish the cause for broken behavior

For a bug, error, regression, stack trace, or unexplained behavior, do not plan from the report's assumed cause. Give the root-cause agent the original symptom and tracker context without a preferred fix, then consume its evidence alongside the explorer and analyst results.

Require a reproducible observation when reasonably possible, a causal chain, rejected alternatives, the smallest responsible fix boundary, and a regression check. If the diagnosis is conditional or unresolved, surface the missing evidence and recommendation at the design gate. Do not disguise an unproven cause as an implementation task.

The planner does not create issues, edit issue bodies, or publish diagnosis through `/prp-debug`. Its only tracker write is publishing and verifying its completed plan under step 8.

For requests that do not assert broken current behavior, skip this step.

## 4. Reason from invariants and primitives

Read `references/planning-craft.md` and challenge the first plausible design before committing to it.

Answer:

1. What observable outcome is actually required?
2. Which existing primitive comes closest to satisfying it?
3. Can configuration, composition, prompting, or a small extension solve it?
4. What assumption forces new state, lifecycle, abstraction, or subsystem?
5. Can that assumption be tested cheaply?
6. What machinery disappears if the simpler mechanism works?

Prefer the smallest valuable vertical slice: it must deliver or directly unlock the user outcome, not merely create an elegant technical primitive. Reuse proven primitives, keep ownership clear, and avoid speculative flexibility. Simplicity is not fewer plan details; it is fewer moving parts in the proposed system.

## 5. Research or spike only when it can change the plan

External research is conditional. Use `prp-core:web-researcher` when current documentation, dependency versions, platform behavior, security guidance, or an unfamiliar tool affects the design. Ask a narrow question tied to the architectural decision and prefer primary sources.

Delegate `/prp-spike` to a separate agent before finalizing when an uncertain, falsifiable claim materially changes the architecture, especially when:

- a new subsystem exists only because external behavior is uncertain;
- a recent or unfamiliar tool may already expose the needed primitive;
- a configuration switch, prompt, or composition technique might remove substantial code;
- competing approaches have dramatically different complexity;
- a small behavioral experiment can prove the real integration-point behavior.

The planner chooses the question. Use the exact agent-delegation prompt under `references/planning-craft.md` → **Decide when to spike**, wait for that agent, then consume its verdict and evidence. Never build the spike in the planner context or copy spike code into the plan as production code.

## 6. Hold the design gate

Before writing the plan, state the recommended approach and its evidence. Stop and ask the user when:

- a missing primitive should probably be built first;
- product intent or the success signal remains too uncertain to justify implementation;
- evidence contradicts the requested implementation;
- the simpler solution materially changes the intended product contract;
- an unresolved decision would create substantially different plans.

Explain the invariant, discovery, recommendation, and cost of the alternatives. Do not bury a load-bearing decision in the artifact.

Minor uncertainties may remain in the plan only with a recommendation, supporting evidence, and the consequence of choosing differently.

## 7. Write the adaptive plan

Resolve the canonical store and save the plan to `$PRP_DIR/plans/<kebab-case-name>.plan.md`:

```bash
# --- PRP store resolver (canonical; keep byte-identical across skills) ---
_gd="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"
case "$_gd" in */.git) _root="${_gd%/.git}" ;; "") _root="$PWD" ;; *) _root="$_gd" ;; esac
_root="$(cd "$_root" && pwd -P)"
_name="$(basename "$_root" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-*//;s/-*$//')"
PRP_DIR="${PRP_HOME:-$HOME/.prp}/${_name:-project}-$(printf %s "$_root" | git hash-object --stdin | cut -c1-8)"
mkdir -p "$PRP_DIR"; [ -f "$PRP_DIR/project.json" ] || printf '{"path": "%s", "name": "%s"}\n' "$_root" "${_name:-project}" > "$PRP_DIR/project.json"
mkdir -p "$PRP_DIR/plans"
```

Read `templates/plan-template.md` and `references/task-format.md`. Keep its required human-scannable spine; assign a stable plan ID, reusing it when revising the same plan, set the source issue metadata when planning from a tracker, and include conditional sections only when they add information. The source metadata is the store lookup key; do not add a separate plan index that can drift.

Use `references/visuals.md` when either applies:

- interaction or user-flow change → before/after UX diagram;
- architecture, ownership, state, or data-flow change → architecture diagram.

When existing users, behavior, or stored data can be affected, include one compact Delivery Considerations section covering only what applies: discoverability, compatibility, rollout, migration, observability, reversibility, documentation, or communication.

Tasks describe outcomes in dependency order. Each task identifies its files and integration points, applicable precedent, implementation detail, tests, and focused validation. Acceptance criteria state the observable completed behavior once, and the validation gates prove those criteria. Use commands verified from this repository, not a generic language catalog.

The plan must make incomplete work unacceptable: every requested outcome is covered, and every validation has an owner. If something cannot be completed in this implementation, resolve the scope with the user before presenting the plan as ready.

## 8. Verify and hand off

If the input came from an issue, publish the complete rendered plan to that issue through the configured tracker access. Prefix the body with `<!-- prp-plan-id: <plan-id> -->`, capture its stable comment URL, record that URL as `Plan Publication` in the local plan, and update the published comment to the same final plan. Read the issue back and verify the complete final plan exists at that URL. If publication or verification fails, preserve the local plan but report the publication blocker; do not claim the shared handoff is complete.

Before reporting completion, verify:

- the invariant and recommended solution are explicit;
- implementation acceptance is distinct from the product success signal;
- the approach is supported by codebase evidence and any relevant spike or research;
- bug-fix plans state the proven causal chain, fix boundary, and regression proof, or clearly surface the evidence still missing;
- tasks cover the full agreed scope and can execute top-to-bottom;
- acceptance criteria cover the observable completed outcome without duplicating a completion checklist;
- decisive references use real paths and line numbers;
- tests prove behavior rather than implementation trivia;
- validation commands exist in the project and cover the integrated outcome;
- diagrams are present when they materially improve human review;
- applicable rollout, compatibility, migration, observability, and reversibility concerns are owned by tasks or explicitly resolved;
- open decisions carry recommendations and none silently change the architecture;
- issue-derived plans account for relevant comments and linked tracker context rather than relying on the body alone;
- issue-derived plans are published in full, verified on the source issue, and record that publication URL;
- no placeholders, generic examples, confidence scores, or arbitrary coverage targets remain.

If the input came from a PRD, invoke `/prp-prd-update planned` with the PRD path, selected phase, and absolute plan path. Verify that the phase is `in-progress` and links to the plan.

Read `templates/report-format.md` and report the recommendation, absolute plan path, source PRD or issue when applicable, evidence or spike used, visuals included, and the next step.

## Resources

- `references/planning-craft.md` — invariant, primitive, simplicity, spike, and decision-gate reasoning
- `references/agent-prompts.md` — adaptive prompts for the planner's evidence-gathering agents
- `references/task-format.md` — implementation task content and sizing
- `references/visuals.md` — conditional UX and architecture diagrams
- `templates/plan-template.md` — adaptive plan artifact
- `templates/report-format.md` — concise user handoff
- `workflows/update-references.md` — bidirectional plan linking mode
