# Subagent Prompts — Intelligence Gathering

> **Kild lane:** you are running inside a kild room, in a workspace (worktree + branch) the kild engine assigned. The driver owns isolation and publishing — SKIP any step below that creates or switches branches or worktrees, pulls or rebases the base branch, pushes, opens PRs, or moves/archives plan artifacts, and never run `gh pr checkout`. Your job ends at implement → validate → commit in the current workspace, reporting evidence. Where a step spawns subagents, do that analysis inline — or ask the room's orchestrator to invite a helper agent.

The exact prompt text for every subagent launch in Phases 2, 3, and 5. Fill the `[bracketed]` slots before sending; do not otherwise reword the prompts.

## Phase 2 — codebase-explorer prompt

Do the `codebase-explorer` analysis below inline (kild lane: no subagents):

```
Find all code relevant to implementing: [feature description].

LOCATE:
1. Similar implementations - analogous features with file:line references
2. Naming conventions - actual examples of function/class/file naming
3. Error handling patterns - how errors are created, thrown, caught
4. Logging patterns - logger usage, message formats
5. Type definitions - relevant interfaces and types
6. Test patterns - test file structure, assertion styles, test file locations
7. Configuration - relevant config files and settings
8. Dependencies - relevant libraries already in use

Categorize findings by purpose (implementation, tests, config, types, docs).
Return ACTUAL code snippets from codebase, not generic examples.
```

## Phase 2 — codebase-analyst prompt

Do the `codebase-analyst` analysis below inline (kild lane: no subagents):

```
Analyze the implementation details relevant to: [feature description].

TRACE:
1. Entry points - where new code will connect to existing code
2. Data flow - how data moves through related components
3. State changes - side effects in related functions
4. Contracts - interfaces and expectations between components
5. Patterns in use - design patterns and architectural decisions

Document what exists with precise file:line references. No suggestions or improvements.
```

## Phase 3 — web-researcher prompt

Do the `web-researcher` analysis below inline (kild lane: no subagents):

```
Research external documentation relevant to implementing: [feature description].

FIND:
1. Official documentation for involved libraries (match versions from package.json: [list relevant deps and versions])
2. Known gotchas, breaking changes, deprecations for these versions
3. Security considerations and best practices
4. Performance optimization patterns

VERSION CONSTRAINTS:
- [library]: v{version} (from package.json)
- [library]: v{version}

Return findings with:
- Direct links to specific doc sections (not just homepages)
- Key insights that affect implementation
- Gotchas with mitigation strategies
- Any conflicts between docs and existing codebase patterns found in Phase 2
```

## Phase 5 — architecture deep-dive prompt

Do the `codebase-analyst` analysis below inline (kild lane: no subagents):

```
Analyze the architecture around these integration points for: [feature description].

INTEGRATION POINTS (from Phase 2):
- [entry point 1 from explorer/analyst findings]
- [entry point 2]

ANALYZE:
1. How data flows through each integration point
2. What contracts exist between components
3. What side effects occur at each stage
4. What error handling patterns are in place

Document what exists with precise file:line references. No suggestions.
```
