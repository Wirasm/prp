# Investigation: Add CLAUDE-GOLANG.md

**Issue**: #11 (https://github.com/Wirasm/PRPs-agentic-eng/issues/11)
**Type**: ENHANCEMENT
**Investigated**: 2026-07-15T12:00:00Z

### Assessment

| Metric     | Value  | Reasoning                                                                                                          |
| ---------- | ------ | ------------------------------------------------------------------------------------------------------------------ |
| Priority   | MEDIUM | Explicitly requested by a user and left open by the owner as "PR welcome", but not blocking any other work.        |
| Complexity | LOW    | One new self-contained markdown file in `claude_md_files/`; the directory is outside the plugin sync and no other file enumerates its contents. |
| Confidence | HIGH   | Eight existing `CLAUDE-*.md` examples define the structure, tone, and depth to mirror; Go conventions are stable and well-documented. |

---

## Problem Statement

`claude_md_files/` ships framework-specific `CLAUDE.md` examples (Rust, Python, Java x2, Node, React, Next.js, Astro) but has no Go variant. Issue #11 asks for a `CLAUDE-GOLANG.md` so Go developers get the same drop-in guidance file the other stacks have. The repo owner left the issue open and welcomes a contribution.

---

## Analysis

### Change Rationale

The existing files are opinionated, battle-tested "how Claude should work in this stack" guides. A Go variant fills the most visible gap in the set (Go is a top-10 language with strong, canonical community conventions — gofmt, table-driven tests, error wrapping — which makes an opinionated file straightforward to encode faithfully).

### Affected Files

| File                                | Lines | Action | Description                                        |
| ----------------------------------- | ----- | ------ | -------------------------------------------------- |
| `claude_md_files/CLAUDE-GOLANG.md`  | NEW   | CREATE | Go-specific Claude Code guidance, mirroring peers  |

### Integration Points

- `CLAUDE.md:31` and `CONTRIBUTING.md:22` reference `claude_md_files/` generically ("Rust, Python, Node, React, …") — no enumeration to update.
- `plugins/prp-core/` sync does **not** include `claude_md_files/` — `python3 scripts/sync_plugin.py --check` must still pass untouched (verify before PR).
- No open PR addresses issue #11.

### Git History

- Directory last touched by 09d238f ("docs: add comprehensive Rust development guidelines") and 0703924 ("docs: add ripgrep enforcement rules to all framework CLAUDE.md files").
- **Implication**: every framework file carries the ripgrep enforcement section — the Go file must include it too.

---

## Implementation Plan

### Step 1: Create `claude_md_files/CLAUDE-GOLANG.md`

**File**: `claude_md_files/CLAUDE-GOLANG.md`
**Action**: CREATE

Mirror `CLAUDE-PYTHON-BASIC.md` (the cleanest exemplar: emoji section headers, prescriptive MUST/NEVER voice, real code examples, ~550-760 lines) with Go-specific content:

1. **Header** — "comprehensive guidance to Claude Code when working with Go (1.24+) code"
2. **Core Development Philosophy** — KISS, YAGNI, key Go proverbs (clear over clever, errors are values, share memory by communicating)
3. **Code Structure & Modularity** — file/function limits, standard layout (`cmd/`, `internal/`, avoid premature `pkg/`), package naming
4. **Development Environment** — Go toolchain, `go mod` (incl. 1.24 `tool` directive), dev commands (`go build ./...`, `go vet`, `golangci-lint`, `gofumpt`, `govulncheck`)
5. **Style & Conventions** — gofmt is law, MixedCaps naming, `-er` interfaces, accept interfaces / return structs, `context.Context` first param, doc comments
6. **Error Handling** — sentinel errors, custom error types, `%w` wrapping, `errors.Is/As`, no panic in libraries — with real code examples
7. **Testing Strategy** — table-driven tests, subtests, `t.Helper`, race detector, coverage target
8. **Concurrency** — goroutine ownership/leaks, channels vs mutexes, `errgroup`, context cancellation
9. **Configuration** — env-based config example
10. **Logging** — `log/slog` structured logging
11. **Git Workflow** — branch strategy + commit format incl. the "never include claude code in commit messages" rule (mirrors Python file)
12. **Security** — `govulncheck`, parameterized queries, input validation
13. **Pre-commit Checklist** and **Critical Guidelines (Non-Negotiable)**
14. **Search Command Requirements** — the ripgrep enforcement section verbatim in spirit (required across all framework files per 0703924)
15. **Useful Resources** — Effective Go, Go Code Review Comments, Google Go Style Guide, golangci-lint

**Why**: matches issue request exactly; structure/tone parity keeps the set coherent.

---

## Patterns to Follow

- Section skeleton, emoji headers, and prescriptive voice: `claude_md_files/CLAUDE-PYTHON-BASIC.md:1-758`
- Pre-commit checklist + "Critical Guidelines (Non-Negotiable)" numbered list: `claude_md_files/CLAUDE-RUST.md:218-241`
- Ripgrep "Search Command Requirements" block: `claude_md_files/CLAUDE-PYTHON-BASIC.md:709-740`

---

## Edge Cases & Risks

| Risk/Edge Case                                             | Mitigation                                                                 |
| ---------------------------------------------------------- | -------------------------------------------------------------------------- |
| Stating a Go version/feature inaccurately                  | Target "Go 1.24+" and only cite stable, long-shipped features              |
| Owner wants "battle-tested" opinions, not generic filler   | Encode canonical community standards (gofmt, table tests, error wrapping) rather than inventing novel opinions |
| Accidentally breaking plugin sync                          | `claude_md_files/` is not synced; run `sync_plugin.py --check` to prove it |

---

## Validation

### Automated Checks

```bash
python3 scripts/sync_plugin.py --check   # must pass untouched (SD-3)
```

### Manual Verification

1. Diff structure against `CLAUDE-PYTHON-BASIC.md` — same major sections adapted to Go.
2. All Go code snippets are syntactically valid.
3. Ripgrep enforcement section present.

---

## Scope Boundaries

**IN SCOPE:**

- Creating `claude_md_files/CLAUDE-GOLANG.md`

**OUT OF SCOPE (do not touch):**

- Other `claude_md_files/*.md` (no retro-edits)
- README / CONTRIBUTING enumeration changes (none exist)
- Plugin (`plugins/prp-core/`) — directory not part of it
- `old-prp-commands/` — reference only

---

## Metadata

- **Investigated by**: Claude
- **Timestamp**: 2026-07-15T12:00:00Z
- **Artifact**: `.claude/PRPs/issues/issue-11.md`
