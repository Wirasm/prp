# Planning Craft — Invariants, Primitives, and Evidence

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

## Choose foundations before logic

Generated code is cheap; structural decisions are expensive to reverse. Get the foundational data
shape and owner right before planning logic around them. Trace the dominant access paths, converge core
types and representations, and keep each decision at one source of truth. A late data-shape change is
often a rewrite; early, it may be one line.

When integrating a new requirement, derive the counterfactual design first: if the requirement had
been foundational from day one, what would the system look like? Read the affected design
holistically and use that answer to expose bolt-ons, stale representations, and misplaced ownership.
It is a reference shape, not automatic permission for a broad rewrite. Plan the smallest safe
increment toward it, and carry the changed concept through every affected type, contract, caller,
test, example, document, and rationale rather than leaving the old model half-alive.

Search from cheapest to most structural:

1. Existing configuration or supported behavior.
2. Composition of existing commands, prompts, APIs, or components.
3. A small extension to an owned primitive.
4. A new abstraction with a clear owner.
5. A new subsystem and lifecycle.

Choose the first shape that satisfies the invariant cleanly and can be validated authoritatively, not
the first familiar pattern. Treat these as signs of a missing primitive:

- the same policy or representation must be maintained at several entry points;
- state or a decision has no obvious owner;
- a new signal must be threaded through types, schemas, pipelines, or layers that do not own it;
- a feature-specific mechanism imitates a domain operation that should be general;
- compatibility logic, lifecycle, cleanup, recovery, or synchronization dominates the outcome.

When a missing primitive is load-bearing, recommend building it first and explain what it unlocks.
Each increment should land one coherent abstraction or deepen one that already exists, not spread a
new capability across callers as special-case coordination.

Before sharing state between actors, ask what happens if another actor modifies it concurrently. If
the answer is not “nothing,” isolate ownership rather than planning more synchronization by default.

## Apply the laziness test

Prefer deletion, direct control flow, shallow call paths, clear ownership, and one resolved decision
over pass-through helpers or policy repeated across layers. DRY shared structure and data models, not
every repeated line; explicit repetition can be simpler than a premature abstraction.

For every proposed abstraction, state store, background process, configuration surface, scaffold, or
defensive path, ask which invariant requires it, what evidence rules out the smaller primitive, what
new failure modes it creates, and what disappears if it is removed. Remove dead weight first. Add
shared types, test infrastructure, CI, or other scaffold early only when it simplifies and supports
the work that follows; do not build defenses or tests around unsupported hypothetical behavior.

Creative solutions often come from testing the observable mechanism directly: toggle a configuration
field, remove an advertised capability, compose existing commands, inject a minimal prompt, or
exercise the real boundary with a tiny fixture. Simplicity means fewer states, representations,
concepts, synchronization points, and ownership boundaries—not merely fewer lines.

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
