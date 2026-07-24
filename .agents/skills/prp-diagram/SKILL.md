---
name: prp-diagram
description: Generate a mermaid-only visual supplement for a plan artifact - the data-model, architecture, and flow diagrams a human wants when absorbing a plan. Use when the user wants to "diagram this plan", "visualize the plan", "draw the plan's architecture", "make diagrams for this plan", or invokes $prp-diagram.
---

> **Arguments:** `$ARGUMENTS` (and `$1`, `$2`, ...) refer to the arguments given when this skill was invoked. Take them from the user's request; if absent, infer them from the conversation.

# PRP Diagram — Visual Supplement for a Plan

**Input**: $ARGUMENTS — a path to a plan/PRD markdown file. If blank, use the most recent file in `$PRP_DIR/plans/`.

One agent, one pass, no subagents. Read the plan, produce the diagrams a human wants beside it while absorbing it. Nothing else.

## Resolve the store

```bash
# --- PRP store resolver (canonical; keep byte-identical across skills) ---
_gd="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"
case "$_gd" in */.git) _root="${_gd%/.git}" ;; "") _root="$PWD" ;; *) _root="$_gd" ;; esac
_root="$(cd "$_root" && pwd -P)"
_name="$(basename "$_root" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-*//;s/-*$//')"
PRP_DIR="${PRP_HOME:-$HOME/.prp}/${_name:-project}-$(printf %s "$_root" | git hash-object --stdin | cut -c1-8)"
mkdir -p "$PRP_DIR"; [ -f "$PRP_DIR/project.json" ] || printf '{"path": "%s", "name": "%s"}\n' "$_root" "${_name:-project}" > "$PRP_DIR/project.json"
```

## Output path

`<plan-basename>.diagrams.md` — strip the plan filename's trailing `.md`, append `.diagrams.md`.

- Plan lives inside `$PRP_DIR` → write NEXT TO it (same directory).
- Plan lives anywhere else → write to `$PRP_DIR/plans/` (`mkdir -p "$PRP_DIR/plans"`).

Overwrite on re-run without asking — this is a derived artifact; the plan is the source of truth.

## Content policy (strict)

The file contains ONLY:

1. A single title line: `# <plan title> — Diagrams`
2. Per diagram: one bold caption line (`**<what this shows>**`), then one ```mermaid fence.

No prose paragraphs, no recommendations, no analysis, no legend sections. Diagrams supplement the plan — they never editorialize it.

## Choosing diagrams

Diagram only what the plan actually contains — never invent entities, flows, or states the plan doesn't describe. Skip any category the plan doesn't support.

| Plan content | Diagram type |
|---|---|
| Data-model changes (tables, entities, types, relations) | `erDiagram` or `classDiagram` |
| Architecture/component changes | `flowchart` — before/after subgraphs when the plan describes both states |
| Key flows (request paths, pipelines, interactions) | `sequenceDiagram` |
| Lifecycle/state rules | `stateDiagram-v2` |

Keep each diagram legible: ~40 nodes max — split into two diagrams rather than cram one. Mermaid syntax must be valid: prefer simple constructs over clever ones, and quote labels containing special characters (`A["label (with) specials"]`).

## HTML alternative

Only when the user explicitly asks for `.html`: write a single self-contained html file at the same path with `.diagrams.html` instead. Same content policy — a title, then per diagram a caption and a `<pre class="mermaid">` block. Do NOT embed or link mermaid.js (no CDN, no scripts) — the consuming UI provides the renderer; add an html comment noting that.

## Report

One line to the user: the expanded absolute output path plus which diagram types were produced.
