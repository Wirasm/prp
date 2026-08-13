# Planning Craft — Invariants, Primitives, and Evidence

> **Kild lane:** you are running inside a kild room, in a workspace (worktree + branch) the kild engine assigned. The driver owns isolation and publishing — SKIP any step below that creates or switches branches or worktrees, pulls or rebases the base branch, pushes, opens PRs, or moves/archives plan artifacts, and never run `gh pr checkout`. Your job ends at implement → validate → commit in the current workspace, reporting evidence. Where a step spawns subagents, do that analysis inline — or ask the room's orchestrator to invite a helper agent.

The planner's highest-leverage decision is usually what not to build. Requirements often arrive bundled with a proposed mechanism; separate the outcome from that mechanism before designing.

## Protect product intent

Planning should preserve a known product decision, not manufacture one. Establish who experiences the problem, what behavior or outcome should change, and whether the proposed scope solves that job or only the local ticket.

Keep three concepts distinct:

- **Invariant** — what every acceptable implementation must keep true.
- **Acceptance** — what proves the agreed implementation is complete.
- **Success signal** — what would show the delivered change improved the product outcome.

A success signal may be quantitative or qualitative: fewer workarounds, a workflow completed without support, an operator no longer repeating configuration, or a measurable change already named by the product context. Never invent a persona, business case, or metric to make the plan look complete. When product intent is unresolved, recommend returning to the PRD or asking the user before technical choices harden the assumption.

## Plan the smallest valuable slice

The smallest technical change is not automatically the smallest valuable change. Prefer a vertical slice that reaches an observable user or operator outcome.

A foundational primitive may come first when it removes structural workarounds, but make the relationship explicit: what product outcome it unlocks, why the feature should not be built safely without it, and what follow-up delivers that value. Avoid plans that end at infrastructure while implying the user's job is complete.

## Find the invariant

Express the requirement as an observable statement that remains true across possible implementations.

- Proposed mechanism: “Build a per-run skill allowlist and isolated skill directory.”
- Invariant: “The agent is not told about undeclared skills, while explicitly requested skills remain usable.”

The invariant names the behavior the user needs. It does not prematurely name storage, services, abstractions, or lifecycle.

Ask:

- What must a user or adjacent system observe?
- Which properties must remain unchanged?
- Which constraints are product decisions, and which are assumptions about the current implementation?
- At which process, layer, or interface can the invariant actually be observed?

## Search for primitives

A primitive is an existing capability that can compose into the outcome: a configuration switch, command, API, prompt contract, event, schema field, state transition, extension point, or established domain operation.

Search from cheapest to most structural:

1. Existing configuration or supported behavior.
2. Composition of existing commands, prompts, APIs, or components.
3. A small extension to an owned primitive.
4. A new abstraction with a clear owner.
5. A new subsystem and lifecycle.

Do not choose the first item blindly. Choose the first one that satisfies the invariant cleanly and can be validated authoritatively.

## Detect missing primitives

Warning signs that the requested feature is working around a missing foundation:

- the same policy must be reimplemented at several entry points;
- state has no obvious owner;
- a feature-specific mechanism imitates a domain operation that should be general;
- compatibility logic dominates the requested behavior;
- the plan needs lifecycle, cleanup, recovery, and synchronization solely to emulate a simpler capability.

When a missing primitive is load-bearing, recommend building it first and explain what it unlocks. Do not hide that recommendation in risks or agent notes.

## Challenge complexity

For every proposed abstraction, background process, state store, staging directory, or policy layer, ask:

- Which invariant requires this?
- What evidence says an existing primitive cannot satisfy it?
- What new ownership and failure modes does it create?
- What is the smallest credible alternative?
- What would disappear if that alternative worked?

Creative solutions often come from testing the observable mechanism directly: toggle a configuration field, remove an advertised capability, compose existing commands, inject a minimal prompt, or exercise the real boundary with a tiny fixture.

## Decide when to spike

Use a spike when all are true:

- the claim is uncertain and falsifiable;
- it materially changes the architecture or scope;
- a small experiment can provide stronger evidence than more prose.

The planner owns the question; a separate agent owns the experiment. Frame the spike around the architectural hinge, not the full feature, then send another agent:

```text
Run the prp-spike skill against: <falsifiable question chosen by the planner>.

The invariant is: <required observable outcome>.
Test the cheapest credible mechanism at <real observation point>, including whether an existing primitive avoids new production machinery. Return the verdict, decisive evidence, and absolute spike report path.
```

Wait for the agent and use the report as planning evidence. Keeping spike execution outside the planner context preserves the planner's synthesis context and gives the disposable experiment its own worktree and lifecycle.

Do not spike settled implementation details, and do not let a spike grow into a prototype of the preferred architecture.

## Surface decisions with meaning

Every unresolved item must say:

- the decision;
- the planner's recommendation;
- the evidence or reasoning;
- what changes if the user chooses differently;
- the safe default, if deferral is genuinely harmless.

If the decision changes product behavior, architecture, or foundational primitives, ask before finalizing. The plan artifact is not a hiding place for decisions the human needs to make.

## Consider delivery conditionally

When a change affects existing users, behavior, or stored data, determine only the applicable concerns:

- discoverability and adoption;
- compatibility with existing behavior;
- rollout posture and affected cohorts;
- data or workflow migration;
- observability after release;
- safe reversal or rollback;
- documentation or communication.

These are questions, not mandatory headings. Put concrete work into implementation tasks and omit concerns that genuinely do not apply.
