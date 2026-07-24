---
name: prp-research-team
description: Design a dynamic research team and plan using agent teams -- analyzes question, composes team, creates executable research plan. Use when the user wants to plan multi-agent research on a question or topic, or invokes /prp-research-team.
argument-hint: <research question or topic> [--orchestration "guidance for team composition"]
---

# PRP Research Team Planner

**Input**: $ARGUMENTS

---

## Mission

Design a dynamic team of research agents and a structured research plan for any given question or topic. The plan targets Claude Code's experimental **agent teams** feature (TeamCreate, shared task list, delegate mode).

**Core Principle**: PLAN ONLY — no research is executed. Produce a comprehensive, executable research plan that enables a team of agents to deliver thorough findings.

**Golden Rule**: Every researcher must have a clear focus, measurable completion criteria, and a defined output format. No vague mandates.

**Doctrine**: The research question dictates the team — never force a fixed roster. A market research question demands different expertise than a codebase architecture question.

---

## Variables

| Variable | Source | Default |
|----------|--------|---------|
| `$ARGUMENTS` | User input | — (required) |
| `ORCHESTRATION` | `--orchestration "..."` flag in $ARGUMENTS | Empty (auto-compose) |
| `OUTPUT_DIR` | Fixed | `$PRP_DIR/research-plans/` |

---

## Phase 1: PARSE — Extract Research Question

### 1.1 Parse Arguments

Extract from `$ARGUMENTS`:

- **Research question or topic**: Everything that is NOT a flag
- **Orchestration guidance**: Value after `--orchestration` flag (if present)

**Parsing rules:**
1. Strip `--orchestration "..."` or `--orchestration '...'` from arguments → store as `ORCHESTRATION`
2. Remaining text = research question
3. If question is empty after parsing → STOP with error

### 1.2 Identify Scope Signals

Scan the research question for scope indicators:

| Signal | Example | Implication |
|--------|---------|-------------|
| Comparative ("vs", "compare", "alternatives") | "React vs Vue vs Svelte" | Multiple perspectives needed |
| Evaluative ("best", "optimal", "should we") | "Best approach for real-time sync" | Criteria definition needed |
| Exploratory ("how", "what are", "landscape") | "What are the approaches to..." | Broad survey needed |
| Investigative ("why", "root cause", "debug") | "Why does X fail under Y" | Deep-dive analysis needed |
| Quantitative ("benchmark", "performance", "cost") | "Performance cost of SSR" | Measurement methodology needed |

### 1.3 Validate

**If question is empty or unclear:**
```
Research question required.

Usage:
  /prp-research-team "What are the best approaches for real-time collaboration?"
  /prp-research-team "Compare state management libraries for React" --orchestration "Focus on bundle size and DX"
```

**PHASE_1_CHECKPOINT:**
- [ ] Research question extracted and non-empty
- [ ] `--orchestration` flag parsed (or confirmed absent)
- [ ] Scope signals identified

**GATE**: If the research question is too vague to decompose into sub-questions → STOP and ASK user for clarification.

---

## Phase 2: CLASSIFY — Domain & Complexity

### 2.1 Determine Research Domain

Classify the question into one or more domains:

| Domain | Indicators | Typical Researcher Profiles |
|--------|------------|-----------------------------|
| CODEBASE | References project files, patterns, architecture | Code analyst, pattern extractor, dependency mapper |
| TECHNICAL | Libraries, frameworks, protocols, algorithms | Docs researcher, benchmarker, compatibility analyst |
| MARKET | Products, competitors, pricing, trends | Market analyst, competitive researcher, trend tracker |
| USER_RESEARCH | User needs, behavior, UX, feedback | UX researcher, survey analyst, persona builder |
| ARCHITECTURE | System design, scalability, trade-offs | Systems architect, performance analyst, security reviewer |
| MIXED | Spans multiple domains | Combination of above |

For MIXED domains, identify the primary domain and supporting domains.

### 2.2 Assess Complexity

| Complexity | Criteria | Team Size | Sub-questions |
|------------|----------|-----------|---------------|
| LOW | Single domain, narrow scope, well-defined | 2-3 researchers | 3-4 |
| MEDIUM | 2 domains, moderate scope, some ambiguity | 3-5 researchers | 4-6 |
| HIGH | 3+ domains, broad scope, significant ambiguity | 5-7 researchers | 5-7 |

**Complexity factors:**
- Number of domains involved
- Breadth of the question
- Depth of analysis required
- Number of comparative dimensions
- Whether primary research vs. synthesis

### 2.3 Apply Orchestration Override

If `ORCHESTRATION` is set, adjust:
- Team composition emphasis
- Domain weighting
- Specific expertise requirements
- Any constraints on approach

**PHASE_2_CHECKPOINT:**
- [ ] Primary domain identified with rationale
- [ ] Supporting domains listed (if MIXED)
- [ ] Complexity assessed with team size determined
- [ ] Orchestration guidance applied (if provided)

---

## Phase 3: DECOMPOSE — Sub-Questions

### 3.1 Break Down Research Question

Decompose into 3-7 independently investigable sub-questions.

**Decomposition rules:**
1. Each sub-question must be answerable by a single researcher
2. Sub-questions should cover the full scope of the original question
3. Identify which sub-questions can run in PARALLEL vs. which have DEPENDENCIES
4. Tag each sub-question with its primary domain

### 3.2 Map Dependencies

Create a dependency graph:

```
SQ-1 (foundational) ──┬──► SQ-2 (parallel)
                       ├──► SQ-3 (parallel)
                       └──► SQ-4 (parallel)
                                    │
                                    ▼
                              SQ-5 (synthesis, depends on SQ-2,3,4)
```

**Dependency types:**
- **NONE**: Can start immediately
- **BLOCKED_BY**: Must wait for specific sub-questions
- **INFORMS**: Benefits from but doesn't require other results

### 3.3 Validate Coverage

Check that sub-questions collectively:
- Cover the full scope of the original question
- Don't have significant overlap (some overlap at boundaries is acceptable)
- Include at least one synthesis/integration sub-question

**PHASE_3_CHECKPOINT:**
- [ ] 3-7 sub-questions defined
- [ ] Each sub-question is independently investigable
- [ ] Dependencies mapped (parallel vs. sequential)
- [ ] Full coverage of original question verified
- [ ] At least one synthesis sub-question included

---

## Phase 4: COMPOSE — Design Team Roles

### 4.1 Design Researcher Profiles

For each researcher, define:

| Field | Description |
|-------|-------------|
| **Name** | Descriptive role name (e.g., "API Compatibility Analyst") |
| **Focus** | 1-2 sentence description of their research area |
| **Sub-questions** | Which SQ-IDs they own |
| **Model** | `sonnet` for most research, `opus` for synthesis/complex analysis |
| **Spawn prompt** | Complete instructions for the agent — must be self-contained |
| **Output format** | Exact structure of their deliverable (markdown sections, tables, etc.) |
| **Completion criteria** | Measurable conditions that define "done" |

### 4.2 Spawn Prompt Requirements

Each spawn prompt MUST include:
1. **Role statement**: Who you are and what you're investigating
2. **Research question(s)**: The specific sub-questions assigned
3. **Methodology**: How to approach the research (web search, code analysis, doc review, etc.)
4. **Output format**: Exact markdown structure for findings
5. **Quality bar**: What constitutes sufficient depth
6. **Completion signal**: How to indicate research is complete (update shared task)

### 4.3 Model Selection

| Researcher Type | Recommended Model | Rationale |
|-----------------|-------------------|-----------|
| Data gatherer / doc reviewer | `sonnet` | Efficient for search and extraction |
| Deep analyst / synthesizer | `opus` | Better reasoning for complex analysis |
| Benchmarker / comparator | `sonnet` | Structured comparison tasks |
| Lead researcher / integrator | `opus` | Synthesis across multiple inputs |

### 4.4 Apply Orchestration to Team

If `ORCHESTRATION` is set, verify the team composition aligns with the guidance. Adjust roles, emphasis, or add/remove researchers as needed.

**PHASE_4_CHECKPOINT:**
- [ ] Each researcher has all 7 fields defined
- [ ] Spawn prompts are self-contained (no external context needed)
- [ ] Output formats are specific and structured
- [ ] Completion criteria are measurable
- [ ] Model selection is justified
- [ ] Team covers all sub-questions with no gaps

---

## Phase 5: PLAN — Research Tasks

### 5.1 Create Task List

For each task, define:

| Field | Description |
|-------|-------------|
| **ID** | `RT-{N}` sequential identifier |
| **Title** | Short descriptive title |
| **Assignee** | Researcher name |
| **Type** | RESEARCH / ANALYSIS / SYNTHESIS / REVIEW |
| **Dependencies** | List of RT-IDs that must complete first (or NONE) |
| **Description** | What specifically needs to be done |
| **Acceptance criteria** | How to verify the task is complete |
| **Estimated effort** | LOW / MEDIUM / HIGH |

### 5.2 Task Ordering

1. **Wave 1**: All tasks with no dependencies (parallel)
2. **Wave 2**: Tasks that depend on Wave 1 outputs
3. **Wave 3**: Synthesis and integration tasks
4. **Final**: Review and quality assurance

### 5.3 Define Cross-Cutting Concerns

Identify shared standards across all researchers:
- Citation format and requirements
- Confidence level tagging (HIGH / MEDIUM / LOW with rationale)
- Contradiction handling (when sources disagree)
- Scope boundary enforcement (when to stop digging)

**PHASE_5_CHECKPOINT:**
- [ ] Every sub-question has at least one task
- [ ] Dependencies form a valid DAG (no cycles)
- [ ] Parallel tasks identified for maximum throughput
- [ ] Synthesis task exists to integrate findings
- [ ] Cross-cutting concerns defined

---

## Phase 6: GENERATE — Write Research Plan

### 6.1 Create Output Directory

```bash
# --- PRP store resolver (canonical; keep byte-identical across skills) ---
_gd="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"
case "$_gd" in */.git) _root="${_gd%/.git}" ;; "") _root="$PWD" ;; *) _root="$_gd" ;; esac
_root="$(cd "$_root" && pwd -P)"
_name="$(basename "$_root" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-*//;s/-*$//')"
PRP_DIR="${PRP_HOME:-$HOME/.prp}/${_name:-project}-$(printf %s "$_root" | git hash-object --stdin | cut -c1-8)"
mkdir -p "$PRP_DIR"; [ -f "$PRP_DIR/project.json" ] || printf '{"path": "%s", "name": "%s"}\n' "$_root" "${_name:-project}" > "$PRP_DIR/project.json"

mkdir -p "$PRP_DIR/research-plans"
```

### 6.2 Determine Output Filename

Convert the research topic to kebab-case, truncate to 50 chars max:
- "What are the best approaches for real-time collaboration?" → `real-time-collaboration`
- "Compare React vs Vue vs Svelte for enterprise apps" → `react-vs-vue-vs-svelte-enterprise`

**Output path**: `$PRP_DIR/research-plans/{topic-slug}.research-plan.md` (report the expanded absolute path to the user).

### 6.3 Write State Sentinel

Write the expanded absolute output path to `$PRP_DIR/state/prp-research-team.state` so the Stop hook can validate:

```bash
mkdir -p "$PRP_DIR/state"
printf '%s\n' "$PRP_DIR/research-plans/{topic-slug}.research-plan.md" > "$PRP_DIR/state/prp-research-team.state"
```

Just the file path, one line, no extra content.

### 6.4 Write Research Plan

Write the research plan to the output path using this exact template:

```markdown
# Research Plan: {Research Question}

## Metadata

| Field | Value |
|-------|-------|
| Date | {YYYY-MM-DD} |
| Topic | {short topic name} |
| Domain | {PRIMARY / MIXED: list} |
| Complexity | {LOW / MEDIUM / HIGH} |
| Team Size | {N} researchers |
| Sub-questions | {N} |
| Tasks | {N} |

---

## Research Question

{The original research question, clearly stated and unambiguous.}

{If orchestration guidance was provided:}
**Orchestration**: {The orchestration guidance}

---

## Research Question Decomposition

| ID | Sub-question | Domain | Parallel | Dependencies | Assigned To |
|----|-------------|--------|----------|--------------|-------------|
| SQ-1 | {sub-question text} | {domain} | {yes/no} | {NONE or SQ-IDs} | {researcher name} |
| SQ-2 | ... | ... | ... | ... | ... |

### Dependency Graph

{ASCII dependency diagram showing parallel vs. sequential flow}

---

## Team Composition

### {Researcher 1 Name}

- **Focus**: {1-2 sentence description}
- **Sub-questions**: {SQ-IDs}
- **Model**: {sonnet / opus}
- **Output format**: {description of deliverable structure}
- **Completion criteria**: {measurable conditions}

**Spawn prompt**:
> {Complete, self-contained instructions for this agent. Must include:
> role statement, assigned sub-questions, methodology, output format,
> quality bar, and completion signal. The agent must be able to execute
> with ONLY this prompt — no external context.}

### {Researcher 2 Name}

{Same structure as above}

{Repeat for all researchers...}

---

## Research Tasks

### Wave 1: Foundation (Parallel)

| ID | Title | Assignee | Type | Dependencies | Acceptance Criteria | Effort |
|----|-------|----------|------|-------------|-------------------|--------|
| RT-1 | {title} | {name} | RESEARCH | NONE | {criteria} | {LOW/MED/HIGH} |

### Wave 2: Deep Analysis

| ID | Title | Assignee | Type | Dependencies | Acceptance Criteria | Effort |
|----|-------|----------|------|-------------|-------------------|--------|
| RT-N | {title} | {name} | ANALYSIS | RT-1, RT-2 | {criteria} | {LOW/MED/HIGH} |

### Wave 3: Synthesis

| ID | Title | Assignee | Type | Dependencies | Acceptance Criteria | Effort |
|----|-------|----------|------|-------------|-------------------|--------|
| RT-N | {title} | {name} | SYNTHESIS | RT-... | {criteria} | {LOW/MED/HIGH} |

### Cross-Cutting Concerns

- **Citations**: {format requirements}
- **Confidence levels**: Tag all findings as HIGH / MEDIUM / LOW with rationale
- **Contradictions**: When sources disagree, document both positions with evidence
- **Scope boundaries**: {when to stop investigating a thread}

---

## Team Orchestration Guide

### Prerequisites

This research plan is designed for execution using Claude Code's experimental **agent teams** feature. Before executing:

1. Ensure agent teams is enabled (experimental feature)
2. Review the team composition and adjust if needed
3. Confirm the research question and scope

### Execution Steps

1. **Create team**: Use `TeamCreate` to spawn all researchers defined in Team Composition
2. **Create shared tasks**: Use the shared task list to create all tasks from the Research Tasks section
3. **Set dependencies**: Link tasks with their dependencies so agents pick up work in the correct order
4. **Monitor progress**: Use delegate mode or direct messaging to check on researcher progress
5. **Collect outputs**: Each researcher posts findings to their assigned tasks
6. **Run synthesis**: The synthesis researcher integrates all findings into the final report

### Display Mode

Use **delegate mode** for autonomous execution:
- Researchers work independently on their assigned tasks
- The lead researcher monitors progress and resolves blockers
- Use `SendMessage` to communicate between researchers when dependencies complete

### Communication Patterns

- **Handoff**: When a Wave 1 researcher completes, notify dependent Wave 2 researchers via task updates
- **Clarification**: Researchers can message the lead for scope questions
- **Contradiction**: If two researchers find conflicting information, escalate to lead for resolution

### Plan Approval

Before execution, review:
- [ ] Team composition matches the research domain
- [ ] Spawn prompts are detailed enough for autonomous execution
- [ ] Task dependencies are correct
- [ ] Acceptance criteria are measurable

---

## Acceptance Criteria

Research is complete when ALL of the following are met:

- [ ] Every sub-question (SQ-*) has been investigated and answered
- [ ] Every research task (RT-*) has been completed and meets its acceptance criteria
- [ ] Findings are cited with sources and confidence levels
- [ ] Contradictions are documented with both positions
- [ ] A synthesis document integrates all findings into a coherent answer
- [ ] The original research question is directly answered with evidence

---

## Output Format: Final Report Structure

The final research report (produced during execution, not in this plan) should follow:

1. **Executive Summary** — Direct answer to the research question (2-3 paragraphs)
2. **Key Findings** — Bulleted list of major discoveries
3. **Detailed Analysis** — Section per sub-question with evidence
4. **Comparative Matrix** — If applicable, structured comparison table
5. **Recommendations** — Actionable next steps with confidence levels
6. **Sources** — All references with URLs and access dates
7. **Appendix** — Raw data, extended quotes, additional context
```

**PHASE_6_CHECKPOINT:**
- [ ] Output directory exists
- [ ] State sentinel file written with the expanded absolute output path
- [ ] Research plan file written with ALL required sections
- [ ] All researcher spawn prompts are self-contained
- [ ] All tasks have acceptance criteria
- [ ] Template sections are filled (no placeholders remain)

**GATE**: Do NOT proceed to Phase 7 until the research plan file passes validation — all 6 required sections must be present:
1. `## Research Question`
2. `## Research Question Decomposition`
3. `## Team Composition`
4. `## Research Tasks`
5. `## Team Orchestration Guide`
6. `## Acceptance Criteria`

---

## Phase 7: OUTPUT — Report to User

Display a summary to the user:

```markdown
## Research Plan Created

**File**: `{output path}`
**Question**: {research question}

### Team Composition ({N} researchers)

| Researcher | Focus | Model |
|------------|-------|-------|
| {name} | {1-line focus} | {model} |

### Plan Overview

- **Domain**: {domain classification}
- **Complexity**: {LOW/MEDIUM/HIGH}
- **Sub-questions**: {N}
- **Tasks**: {N} ({W1} parallel → {W2} analysis → {W3} synthesis)

### Execution

To execute this research plan with agent teams:
1. Review the plan: `read {output path}`
2. Create the team and start execution using the orchestration guide in the plan

### Manual Execution Alternative

If agent teams is not available, execute sequentially:
1. Work through Wave 1 tasks in parallel using Task tool subagents
2. Feed Wave 1 outputs into Wave 2 tasks
3. Synthesize in Wave 3
```

**PHASE_7_CHECKPOINT:**
- [ ] Summary displayed to user
- [ ] Team composition table shown
- [ ] Execution instructions provided
- [ ] Output file path clearly communicated

---

## Success Criteria

- **QUESTION_PARSED**: Research question extracted and validated
- **DOMAIN_CLASSIFIED**: Primary and supporting domains identified
- **DECOMPOSED**: 3-7 independent sub-questions with dependency mapping
- **TEAM_DESIGNED**: Each researcher has name, focus, spawn prompt, output format, completion criteria
- **TASKS_PLANNED**: All tasks have IDs, assignees, dependencies, acceptance criteria
- **PLAN_WRITTEN**: Research plan file created with all required sections
- **SENTINEL_SET**: State file written for stop hook validation
- **USER_INFORMED**: Summary with execution instructions displayed
