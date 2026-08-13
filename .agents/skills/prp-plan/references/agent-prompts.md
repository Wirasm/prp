# Planner Subagent Prompts

Adapt these prompts to the feature and known uncertainty. The agents gather evidence; the planner decides what should change.

## Codebase explorer

Use `codebase-explorer`:

```text
Map the code relevant to [problem and observable invariant].

Find the owning entry points, related implementation and tests, configuration, extension points, and the closest existing primitives that could compose into the outcome. Include useful variations where the codebase handles the same concern differently.

Return a concise evidence map with precise file:line references and short actual snippets only where they clarify a contract. Identify repository commands that validate this area. Document what exists; do not design the solution.
```

## Codebase analyst

Use `codebase-analyst`:

```text
Trace how [current behavior related to the invariant] actually works.

Follow control flow, data flow, state ownership, side effects, configuration, and boundaries from [known entry point, if any] to the observable result. Distinguish behavior proved at each layer from assumptions or behavior owned by an external tool.

Return the decisive path with precise file:line references, contracts, and observation points. Document what exists; do not recommend a future design.
```

## Root-cause analyzer

Use `root-cause-analyzer` when the request reports broken current behavior:

```text
Diagnose this reported behavior: [original symptom, error, stack trace, or issue context].

The expected observable invariant is: [expected behavior, if known].

Reproduce it at the cheapest authoritative boundary when reasonably possible. Test competing hypotheses, trace the evidence to the smallest fixable cause, rule out plausible alternatives, and identify the minimum fix boundary plus a regression check. Return explicit uncertainty rather than assuming the report's proposed cause. Do not modify files or publish tracker findings.
```

## Targeted follow-up

Reuse the relevant agent rather than launching a generic architecture phase:

```text
Resolve this remaining planning question: [specific uncertainty].

Inspect [integration points] and report only evidence that changes the answer: ownership, contract, failure behavior, precedent, and exact file:line references. State what the code proves and what remains unknown. Do not propose implementation.
```

## Web researcher

Use `web-researcher` only for an external architectural hinge:

```text
Determine whether [specific product/library/tool and version] supports [primitive or observable behavior]. This answer decides between [simple approach] and [larger approach].

Prioritize official documentation, source, schemas, release notes, and reproducible examples. Separate documented fact from inference. Return direct citations, version/date applicability, the exact control or API if it exists, limitations, and the smallest behavior that still needs an empirical spike. Do not provide a generic best-practices survey.
```

## Prompt quality

- Give each agent the problem and invariant, not a preselected implementation.
- Give the root-cause agent the original symptom and complete tracker context, not the planner's preferred explanation.
- Name the uncertainty that its evidence should reduce.
- Ask for actual observation points when external behavior is involved.
- Do not demand arbitrary counts, exhaustive inventories, or generic security/performance sections.
- Follow up in the same agent context when the first result exposes a sharper question.
