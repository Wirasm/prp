# Adaptive Implementation Plan Template

Keep every **required** section. Include a **conditional** section only when it adds decision or implementation value. Remove all instructional comments and unused placeholders from the saved plan.

---

# {Outcome-oriented plan title}

**Plan ID:** `{stable kebab-case identifier}`
**Source PRD:** `{absolute path | None}`
**PRD Phase:** `{phase number and name | None}`
**Source Issue:** `{tracker reference or URL | None}`
**Plan Publication:** `{verified issue comment URL | None}`

## Outcome

**Problem:** {Specific problem and who experiences it.}

**Affected user:** {User, operator, team, or system experiencing the problem.}

**User outcome:** {What becomes possible or reliably different.}

**Invariant:** {Observable property every acceptable solution must preserve.}

**Success signal:** {Quantitative or qualitative evidence that the delivered change improved the outcome; or `Not measured separately — <why acceptance fully captures this internal outcome>`. Do not invent a metric.}

**Approach:** {Concise description of the chosen solution.}

## Recommendation

{Why this is the simplest coherent approach supported by the codebase. Name the existing primitives it uses and the assumption or evidence that rules out unnecessary machinery.}

### Evidence

- `{file:line}` — {decisive existing behavior, primitive, or convention}
- {Decision-relevant issue comment, linked issue, PR, or specification when the plan came from a tracker}
- {Official source and version, when external behavior matters}
- {Spike verdict and absolute report path, when a spike was run}

### Alternatives considered

<!-- CONDITIONAL: include only meaningful alternatives. -->

- **{Alternative}:** {Why it loses against the invariant, evidence, or ownership cost.}

## Root Cause

<!-- CONDITIONAL: include for a bug, regression, error, stack trace, or unexplained current behavior. -->

- **Observed failure:** {Reproduced symptom and decisive observation.}
- **Causal chain:** {Shortest evidence-backed chain from symptom to cause.}
- **Fix boundary:** `{path:line}` — {smallest responsible behavior to change.}
- **Regression proof:** {Test or procedure that fails before the fix and passes after.}
- **Remaining uncertainty:** {Named condition and resolution step, or `None`.}

## Visuals

<!-- CONDITIONAL: use a UX diagram for interaction changes and/or an architecture diagram for structural changes. Follow references/visuals.md. Omit this section when prose is clearer. -->

## Implementation Context

### Mandatory reading

| File | Why it matters |
|---|---|
| `{path:lines}` | {Primitive, contract, integration point, or test precedent the implementer must understand} |

### Existing patterns and primitives

- **{Pattern or primitive}:** `{path:lines}` — {How it applies; include a short actual snippet only when the shape cannot be conveyed precisely in prose.}

### Integration points

- `{path:line}` — {Current role and how the change connects.}

## Scope

### In scope

- {Agreed outcome}

### Not building

- {Explicit exclusion and why it is outside the invariant or belongs later}

## Delivery Considerations

<!-- CONDITIONAL: include only when existing users, behavior, or stored data may be affected. Keep only applicable rows. -->

| Concern | Decision and owned work |
|---|---|
| Discoverability / adoption | {How affected users learn or adopt the change} |
| Compatibility / migration | {Existing behavior or data transition} |
| Rollout / reversibility | {Release posture and safe rollback} |
| Observability | {How product or operational surprises become visible} |
| Documentation / communication | {Required user-facing or operator material} |

## Implementation

<!-- Follow references/task-format.md. Repeat in dependency order. -->

### 1. {Outcome}

**Files and integration points**
- `{path:line}` — {CREATE / UPDATE and ownership rationale}

**Implementation**
- {Concrete behavior and existing primitive or precedent to use.}
- {Boundary, failure behavior, migration, or compatibility detail when relevant.}

**Tests**
- {Behavior to prove at the appropriate test surface.}

**Validation**
- `{focused command}` — {Expected observable result.}

## Acceptance

State the completed behavioral contract once. Use stable identifiers so tasks and validation can refer to it without duplicating checklists.

1. **AC1 — {Observable outcome}:** {Given/when/then behavior or externally verifiable result.}
2. **AC2 — {Preserved invariant}:** {Behavior that must remain true across the change.}

## Validation

List the repository's authoritative integrated gates in execution order.

| Gate | Command or procedure | Proves |
|---|---|---|
| Focused behavior | `{command}` | {AC1 and task-level behavior} |
| Project gate | `{command}` | {AC2, types, lint, suite, build, or equivalent} |
| Runtime / manual | {Concrete procedure, when automation cannot prove it} | {Acceptance criterion not otherwise observable} |

## Risks and Decisions

<!-- CONDITIONAL: omit when none remain. Minor decisions only; resolve architectural forks with the user before finalizing. -->

| Decision or risk | Recommendation | Evidence / mitigation | Consequence if different |
|---|---|---|---|
| {Question or risk} | {Planner's recommendation} | {Why} | {What changes} |

## Related Plans

<!-- CONDITIONAL: maintained by the update-references workflow. Omit until links exist. -->

- **Depends on:** {absolute plan path + label, or None}
- **Followed by:** {absolute plan path + label, or None}

## Agent Notes

<!-- CONDITIONAL free-form canvas for useful material that does not fit above. Do not use it to hide blockers, scope, or decisions the user needs to see. -->
