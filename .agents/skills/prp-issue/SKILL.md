---
name: prp-issue
description: Investigate a GitHub issue and implement the fix - analyze codebase, create a plan, then code, PR, review by the review agents, and act on their findings. Use when the user wants to investigate or triage a GitHub issue or bug report, fix an investigated issue, implement an issue fix, or invokes $prp-issue.
---

> **Arguments:** `$ARGUMENTS` (and `$1`, `$2`, ...) refer to the arguments given when this skill was invoked. Take them from the user's request; if absent, infer them from the conversation.

# PRP Issue

**Input**: $ARGUMENTS

```bash
# --- PRP store resolver (canonical; keep byte-identical across skills) ---
_gd="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"
case "$_gd" in */.git) _root="${_gd%/.git}" ;; "") _root="$PWD" ;; *) _root="$_gd" ;; esac
_root="$(cd "$_root" && pwd -P)"
_name="$(basename "$_root" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-*//;s/-*$//')"
PRP_DIR="${PRP_HOME:-$HOME/.prp}/${_name:-project}-$(printf %s "$_root" | git hash-object --stdin | cut -c1-8)"
mkdir -p "$PRP_DIR"; [ -f "$PRP_DIR/project.json" ] || printf '{"path": "%s", "name": "%s"}\n' "$_root" "${_name:-project}" > "$PRP_DIR/project.json"
```

Two-phase issue workflow: **investigate** an issue into an implementation artifact, then **fix** it from that artifact (code, PR, agent review, act on findings).

---

## Route on the verb

Read the first token of `$ARGUMENTS` to choose the workflow. Everything after the verb is the issue/artifact argument the workflow operates on.

| First token | Workflow | Operates on |
|-------------|----------|-------------|
| `investigate` | `workflows/investigate.md` | issue number / URL / free-form description |
| `fix` | `workflows/fix.md` | issue number / artifact path (`+ optional --base <branch>`) |
| **both verbs** — `investigate and fix`, `investigate then fix` | `workflows/investigate.md`, **then** `workflows/fix.md` | the issue; the artifact the first phase writes is the second phase's input |
| _no verb_ (a bare issue number, URL, or description) | `workflows/investigate.md` | the whole argument — investigation is the entry point; you investigate before you fix |

**Action**: strip the verb(s), then follow each matching workflow file end-to-end, in the order above.

**Read the workflow file for every phase you run — including the second one.** Both phases asked for
means both files read. Finishing an investigation leaves you holding a plan and feeling ready to
implement it, and implementing from that feeling is the failure this line exists to stop: `fix.md`
carries the branch discipline, the validation gate, the PR, the agent review and the archive, and an
agent that never opened it silently does none of them. It has happened.

**Do not blend them.** Sequential, each run to its end — not interleaved, and not one phase
improvising the other's steps from memory.

---

## Notes

- `investigate` is read-mostly: it analyzes, writes an artifact under `$PRP_DIR/issues/`, and (for GitHub issues) posts a comment.
- `fix` is **side-effecting**: it creates a branch, commits, opens a PR, has the review agents review it, and pushes fixes for what they find. Only run it once an investigation artifact exists.
- Typical flow: `prp-issue investigate <number>` → review the artifact → `prp-issue fix <number>`.
