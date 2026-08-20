---
name: prp-review
description: Reviews GitHub pull requests through specialist review agents, runs repository validation, verifies corrections, aggregates findings, and posts the result. Defaults to code, seam, and simplification review, and adds type design when typed contracts change; the operator can add scopes or explicitly request only selected scopes. Use when the operator asks to review a PR, re-review fixes, check whether a PR is ready to merge, run review agents, or invokes $prp-review.
---

> **Arguments:** `$ARGUMENTS` (and `$1`, `$2`, ...) refer to the arguments given when this skill was invoked. Take them from the user's request; if absent, infer them from the conversation.

# Review a Pull Request

Coordinate an evidence-based PR review. Reviewer agents are the only path for judging the code:
do not add an inline review pass before or after them.

**Input**: $ARGUMENTS (if absent, use the current branch's PR).

Let `workflows/agents.md` own scope selection, reviewer dispatch, correction verification,
aggregation, and publication. Pass the operator's scope intent and flags through without rebuilding
those contracts here.

Resolve the canonical store before starting:

```bash
# --- PRP store resolver (canonical; keep byte-identical across skills) ---
_gd="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"
case "$_gd" in */.git) _root="${_gd%/.git}" ;; "") _root="$PWD" ;; *) _root="$_gd" ;; esac
_root="$(cd "$_root" && pwd -P)"
_name="$(basename "$_root" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-*//;s/-*$//')"
PRP_DIR="${PRP_HOME:-$HOME/.prp}/${_name:-project}-$(printf %s "$_root" | git hash-object --stdin | cut -c1-8)"
mkdir -p "$PRP_DIR"; [ -f "$PRP_DIR/project.json" ] || printf '{"path": "%s", "name": "%s"}\n' "$_root" "${_name:-project}" > "$PRP_DIR/project.json"
```

Read `workflows/agents.md` and execute it end-to-end. Before producing the report, read
`templates/review-report.md` and follow its output contract exactly.

## Resources

- `workflows/agents.md` — PR resolution, validation, agent scopes, aggregation, and publication
- `templates/review-report.md` — canonical local and GitHub review format
