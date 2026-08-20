---
name: prp-review
description: Reviews GitHub pull requests through specialist review agents, runs repository validation, verifies corrections, aggregates findings, and posts the result. Defaults to code, seam, and simplification review, and adds type design when typed contracts change; the operator can add scopes or explicitly request only selected scopes. Use when the operator asks to review a PR, re-review fixes, check whether a PR is ready to merge, run review agents, or invokes $prp-review.
---

> **Arguments:** `$ARGUMENTS` (and `$1`, `$2`, ...) refer to the arguments given when this skill was invoked. Take them from the user's request; if absent, infer them from the conversation.

# Review a Pull Request

Coordinate an evidence-based PR review. Reviewer agents are the only path for judging the code:
do not add an inline review pass before or after them.

**Input**: $ARGUMENTS (if absent, use the current branch's PR).

Run by default:

- `code-reviewer` for a general review of correctness, sanity, scope, and repository fit;
- `seam-analyzer` for missing types, counterpart drift, and bypassed boundaries;
- `code-simplifier` for premature machinery and smaller structures that preserve the outcome.

Also run `type-design-analyzer` when the change materially touches types, schemas,
constructors or factories, public signatures, state variants, or compiler escape hatches. Select it
by reading the change, not by file extension or keyword parsing. Skip it when no typed contract changed.

Interpret scope instructions by intent, not as a command grammar. With no scope instruction, run the
three unconditional defaults plus the conditional type scope when applicable. A named or added scope
augments them: “add tests” means the applicable defaults plus `tests`. An explicit restriction
replaces them: “only tests” means exactly `tests`. Honor any other explicit operator inclusion or
exclusion. `all` selects every scope. Accept the old `--agents` token as a no-op compatibility alias.

`--verify-corrections` is a focused independent re-review. Require the previous canonical report and
reviewed head; verify its findings and dispositions against the current head and correction diff. Do
not repeat a full PR review unless that diff materially changes the outcome, architecture, or scope.

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
