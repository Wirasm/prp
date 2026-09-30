---
name: prp-companion
description: Writes the visual HTML companion of a PRP plan or review - one self-contained page beside the markdown that shows a plan's change diagram, steps and risks, or a review's verdict and findings, with every item carrying a stable id a mark can point at. prp-plan and prp-review run it after writing their markdown. Use when the user wants to "make it visual", "show me the plan", "visualize this review", "diagram this plan", "write the companion", or invokes /prp-companion.
argument-hint: "[path/to/plan-or-review.md] (blank = most recent plan or review in the store)"
---

# PRP Companion

Write one HTML page that lets a human take in a plan or review with less reading. The markdown stays
the artifact that agents and later skills read: never edit it. The page is derived from it and is
overwritten on every run.

**Input**: $ARGUMENTS — a plan (`*.plan.md`) or review report (`pr-*-review.md`). If blank, use the
newest of either in `$PRP_DIR/plans/` and `$PRP_DIR/reviews/`. For any other kind of markdown, say
the companion covers plans and reviews only, and stop.

The agent that just wrote the artifact writes its companion, in the same context. Do not hand it to
a fresh agent.

## Resolve the store

```bash
# --- PRP store resolver (canonical; keep byte-identical across skills) ---
# Adopt the store that already records this root; mint a key only when none does.
_gd="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"
case "$_gd" in */.git) _root="${_gd%/.git}" ;; "") _root="$PWD" ;; *) _root="$_gd" ;; esac
_root="$(cd "$_root" && pwd -P)"
_name="$(basename "$_root" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-*//;s/-*$//')"
_home="${PRP_HOME:-$HOME/.prp}"
_hit="$(grep -lsF "\"path\": \"$_root\"" "$_home"/*/project.json 2>/dev/null | head -1)"
PRP_DIR="${_hit%/project.json}"
[ -n "$PRP_DIR" ] || PRP_DIR="$_home/${_name:-project}-$(printf %s "$_root" | git hash-object --stdin | cut -c1-8)"
mkdir -p "$PRP_DIR"; [ -f "$PRP_DIR/project.json" ] || printf '{"path": "%s", "name": "%s"}\n' "$_root" "${_name:-project}" > "$PRP_DIR/project.json"
```

## Write the page

1. Read the whole markdown artifact.
2. Build the theme `<style>`: `templates/default-theme.css` verbatim, then `$PRP_DIR/companion.css`
   verbatim after it when that file exists, so any token the store's file leaves out keeps its
   default. A host UI that wants pages in its own look writes that file; prp never writes it.
3. Read `templates/companion.md` and follow it exactly.
4. Write the page beside the markdown: same directory, final `.md` replaced by `.html`
   (`x.plan.md` → `x.plan.html`, `pr-12-review.md` → `pr-12-review.html`).
5. Before reporting, check the page against the markdown once: every risk, finding, required outcome
   and acceptance criterion is on the page as the markdown's own words, and nothing on the page is
   absent from the markdown. Fix the page, never the markdown.

## Report

One line: the companion's absolute path.

## Resources

- `templates/companion.md` — the page contract: file rules, fidelity, ids, diagrams, plan and review layouts
- `templates/default-theme.css` — the built-in theme, always pasted first; the store's `companion.css` overrides it
