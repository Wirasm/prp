# Planner Subagent Prompts

> **Kild lane:** you are running inside a kild room, in a workspace (worktree + branch) the kild engine assigned. The driver owns isolation and publishing — SKIP any step below that creates or switches branches or worktrees, pulls or rebases the base branch, pushes, opens PRs, or moves/archives plan artifacts, and never run `gh pr checkout`. Your job ends at implement → validate → commit in the current workspace, reporting evidence. Where a step spawns subagents, do that analysis inline — or ask the room's orchestrator to invite a helper agent.

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
- Name the uncertainty that its evidence should reduce.
- Ask for actual observation points when external behavior is involved.
- Do not demand arbitrary counts, exhaustive inventories, or generic security/performance sections.
- Follow up in the same agent context when the first result exposes a sharper question.
