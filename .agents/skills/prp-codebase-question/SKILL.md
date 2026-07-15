---
name: prp-codebase-question
description: Research codebase questions using parallel agents - documents what exists, not what should change. Use when the user asks how the codebase works, where something lives, or invokes $prp-codebase-question.
---

> **Arguments:** `$ARGUMENTS` (and `$1`, `$2`, ...) refer to the arguments given when this skill was invoked. Take them from the user's request; if absent, infer them from the conversation.

# Codebase Research

**Input**: $ARGUMENTS

---

## Your Mission

Answer codebase questions thoroughly by spawning parallel specialized agents, synthesizing their findings, and producing a research document.

**Core Philosophy**: Document what IS, not what SHOULD BE. You are a technical cartographer.

**Golden Rule**: Every claim must have a `file:line` reference. No speculation, no suggestions, no critique.

---

## CRITICAL: Documentarian Only

- **DO NOT** suggest improvements or changes
- **DO NOT** perform root cause analysis unless explicitly asked
- **DO NOT** propose future enhancements
- **DO NOT** critique implementations or identify problems
- **DO NOT** recommend refactoring or optimization
- **ONLY** describe what exists, where it exists, how it works, and how components interact

---

## Phase 1: PARSE - Understand the Query

### 1.1 Read Mentioned Files

If the user mentions specific files, read them FULLY first (no limit/offset) before any decomposition.

### 1.2 Classify the Query

| Type | Indicators | Agent Focus |
|------|-----------|-------------|
| **Where** | "where is", "find", "locate" | `codebase-explorer` primary |
| **How** | "how does", "trace", "flow" | `codebase-analyst` primary |
| **What** | "what is", "explain", "describe" | Both agents in parallel |
| **Pattern** | "how do we", "convention", "examples" | `codebase-explorer` primary |
| **External** | "docs", "best practice", "API" | Add `web-researcher` |

### 1.3 Determine Scope

- Identify specific components, patterns, or concepts to investigate
- Note any `--web` flag for external research
- Note any `--follow-up` flag for appending to existing research

**PHASE_1_CHECKPOINT:**
- [ ] Mentioned files read in full
- [ ] Query type classified
- [ ] Research scope identified
- [ ] Flags parsed (--web, --follow-up)

---

## Phase 2: DECOMPOSE - Break into Research Areas

### 2.1 Create Research Plan

Break the query into 2-5 composable research areas:

```
RESEARCH QUESTION: {user's question}

AREAS:
1. {Area} → Agent: {which agent}
2. {Area} → Agent: {which agent}
3. {Area} → Agent: {which agent}
```

### 2.2 Agent Selection

| Agent | Use When |
|-------|----------|
| `codebase-explorer` | Finding WHERE code lives, locating files, extracting patterns, discovering conventions |
| `codebase-analyst` | Understanding HOW code works, tracing data flow, mapping integration points |
| `web-researcher` | Only when `--web` flag is set or user explicitly asks for external docs |

**Strategy:**
1. Start with `codebase-explorer` to find what exists
2. Then use `codebase-analyst` on the most relevant findings to trace how they work
3. Run agents in parallel when they're searching for different areas

**PHASE_2_CHECKPOINT:**
- [ ] Query decomposed into 2-5 research areas
- [ ] Agent assigned to each area
- [ ] Parallel vs sequential execution planned

---

## Phase 3: EXPLORE - Spawn Parallel Agents

### 3.1 Launch Codebase Agents

**Launch agents in parallel by spawning them as subagents in one step.**

For each research area, use the appropriate agent:

**`codebase-explorer`:**

```
Find all code relevant to: {research area}

LOCATE:
1. {Specific files/components to find}
2. {Patterns or conventions to extract}
3. {Related test files and configuration}

Categorize findings by purpose. Return ACTUAL code snippets with file:line references.
Remember: Document what exists, no suggestions or improvements.
```

**`codebase-analyst`:**

```
Analyze the implementation of: {research area}

TRACE:
1. {Data flow to trace}
2. {Integration points to document}
3. {Contracts between components}

Document what exists with precise file:line references. No suggestions.
```

### 3.2 Launch Web Research (if --web or explicitly requested)

**`web-researcher`:**

```
Research external documentation for: {topic}

FIND:
1. {Specific documentation needed}
2. {API references or patterns}

Return findings with direct links and citations.
```

### 3.3 Wait for All Agents

**IMPORTANT**: Wait for ALL agents to complete before proceeding.

**PHASE_3_CHECKPOINT:**
- [ ] All agents launched (parallel where possible)
- [ ] All agents completed
- [ ] Results collected from each agent

---

## Phase 4: SYNTHESIZE - Merge Findings

### 4.1 Compile Results

- Prioritize live codebase findings as primary source of truth
- Connect findings across different components
- Include specific `file:line` references throughout
- Document patterns, connections, and architectural decisions as they exist

### 4.2 Answer the Question

Map findings back to the user's original question:

| Question Aspect | Finding | Evidence |
|----------------|---------|----------|
| {aspect 1} | {what was found} | `file.ts:123` |
| {aspect 2} | {what was found} | `file.ts:456` |

### 4.3 Identify Gaps

Note any areas that couldn't be fully documented:

- {Area that needs further investigation}
- {Question that remains open}

**PHASE_4_CHECKPOINT:**
- [ ] All agent results synthesized
- [ ] Findings connected across components
- [ ] Original question answered with evidence
- [ ] Gaps identified

---

## Phase 5: DOCUMENT - Generate Research File

### 5.1 Gather Metadata

```bash
date -u +"%Y-%m-%dT%H:%M:%SZ"
git rev-parse --short HEAD
git branch --show-current
basename $(git rev-parse --show-toplevel)
```

### 5.2 Create Research Directory

```bash
mkdir -p .claude/PRPs/research
```

### 5.3 Determine Filename

**If --follow-up**: Append to existing research file instead of creating new one.

**If new research**:

**Path**: `.claude/PRPs/research/{YYYY-MM-DD}-{kebab-case-topic}.md`

Examples:
- `2025-01-08-authentication-flow.md`
- `2025-01-15-database-migration-patterns.md`

### 5.4 Write Research Document

```markdown
---
date: {ISO timestamp with timezone}
git_commit: {short hash}
branch: {branch name}
repository: {repo name}
topic: "{User's Question/Topic}"
tags: [research, codebase, {relevant-component-names}]
status: complete
last_updated: {YYYY-MM-DD}
---

# Research: {User's Question/Topic}

**Date**: {ISO timestamp}
**Git Commit**: {short hash}
**Branch**: {branch name}
**Repository**: {repo name}

## Research Question

{Original user query}

## Summary

{High-level documentation of what was found, answering the question by describing what exists}

## Detailed Findings

### {Component/Area 1}

- Description of what exists (`file.ts:123`)
- How it connects to other components
- Current implementation details

### {Component/Area 2}

...

## Code References

| File | Lines | Description |
|------|-------|-------------|
| `path/to/file.ts` | 123-145 | {What's there} |
| `another/file.ts` | 45-67 | {What's there} |

## Architecture Documentation

{Current patterns, conventions, and design implementations found}

## Open Questions

- {Areas that need further investigation}
```

### 5.5 Add GitHub Permalinks (if applicable)

```bash
# Check if on main or pushed
git branch --show-current
gh repo view --json owner,name -q '"\(.owner.login)/\(.name)"'
```

If on main/pushed, replace local file references with:
`https://github.com/{owner}/{repo}/blob/{commit}/{file}#L{line}`

### 5.6 Handle Follow-ups

If `--follow-up` flag and existing research file:

1. Read the existing research file
2. Update frontmatter: `last_updated` and add `last_updated_note`
3. Append new section: `## Follow-up Research {timestamp}`
4. Spawn new agents as needed
5. Save updated document

**PHASE_5_CHECKPOINT:**
- [ ] Metadata gathered
- [ ] Research file created (or existing file updated for follow-up)
- [ ] All sections filled with evidence-based content
- [ ] GitHub permalinks added (if applicable)
- [ ] No placeholder values remain

---

## Phase 6: OUTPUT - Present to User

```markdown
## Research Complete

**Question**: {original question}
**Document**: `.claude/PRPs/research/{filename}.md`

### Summary

{2-3 sentence answer to the question}

### Key Findings

- **{Finding 1}**: {brief} (`file.ts:123`)
- **{Finding 2}**: {brief} (`file.ts:456`)
- **{Finding 3}**: {brief} (`file.ts:789`)

### Architecture

{1-2 sentence description of relevant architecture}

### Open Questions

- {Any unanswered aspects}

### Follow-up

To dig deeper: `$prp-codebase-question --follow-up {topic}`
To include external docs: `$prp-codebase-question --web {topic}`
```

---

## Usage Examples

```bash
# Basic codebase question
$prp-codebase-question how does authentication work

# Include external documentation
$prp-codebase-question --web how does the PRP runner execute commands

# Follow up on previous research
$prp-codebase-question --follow-up what error handling patterns exist in the runner

# Locate and document a specific area
$prp-codebase-question where are all the command templates and how are they structured
```

---

## Critical Reminders

1. **Document, don't evaluate.** Describe what IS, never what SHOULD BE.

2. **Evidence required.** Every claim needs a `file:line` reference.

3. **Agents are parallel.** Launch multiple agents simultaneously when researching different areas.

4. **Wait for completion.** Never synthesize until ALL agents have returned.

5. **Read first.** If the user mentions files, read them fully before spawning agents.

6. **No placeholders.** Every field in the research document must have real values.

7. **Codebase is truth.** Live code always overrides documentation or assumptions.

---

## Success Criteria

- **QUESTION_ANSWERED**: User's question addressed with concrete evidence
- **AGENTS_USED**: Specialized agents spawned for each research area
- **EVIDENCE_COMPLETE**: Every finding has `file:line` references
- **DOCUMENT_CREATED**: Research file saved at `.claude/PRPs/research/`
- **NO_OPINIONS**: Document describes what exists, not what should change
- **PERMALINKS_ADDED**: GitHub links included when possible
