---
name: prp-review
description: Reviews GitHub pull requests through specialist review agents, runs repository validation, aggregates findings, and posts the result. Always uses the code reviewer and seam analyzer; add tests, comments, errors, types, docs, or simplify when the user requests those scopes. Use when the user asks to review a PR, check whether a PR is ready to merge, run review agents, or invokes /prp-review.
argument-hint: "<pr-number|pr-url|branch> [tests|comments|errors|types|docs|simplify|all] [--approve|--request-changes]"
---

# Review a Pull Request

Coordinate an evidence-based PR review. Reviewer agents are the only path for judging the code:
do not add an inline review pass before or after them.

**Input**: $ARGUMENTS (if absent, use the current branch's PR).

Always run:

- `prp-core:code-reviewer` for correctness, project rules, and high-confidence defects;
- `prp-core:seam-analyzer` for missing types, counterpart drift, and bypassed boundaries.

Named scopes are additive. Run their specialist agents only when explicitly requested; `all` adds
every specialist. Accept the old `--agents` token as a no-op compatibility alias.

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
