# PRP Home Reshape — move all PRP artifacts and state to `~/.prp/<project-key>/`

**Goal**: PRP artifacts (plans, prds, research, reviews, reports, issues, debug, orchestration) and PRP runtime state (loop state, verdicts, hook sentinels) move OUT of consuming repos (`.claude/PRPs/` and `.claude/prp-*.state*`) into a per-project store under the user home. PRP skills, agents, and templates (the "intelligence") stay exactly where they are.

**Why (decided, do not relitigate)**: no gitignore dance, no repo pollution, works in repos the user doesn't control, and — the structural bug — gitignored in-repo files never reach git worktrees, so worktree-based agents (prp-orchestrate, agent-tool `isolation: "worktree"`, kild rooms) could never see the project's PRP artifacts. A home store keyed by the *main checkout* is shared by every worktree of the project by construction.

**Hard design rule (from the human, overrides earlier framing)**: PRP and kild have ZERO dependency on each other, in either direction. Nothing in PRP core (skills, scripts, resolver, `~/.prp` layout) may reference kild, read kild config, or honor kild env vars. See Appendix B for the one place integration may be mentioned — and who owns it (not PRP).

**Executor notes**: this repo's distribution targets (`plugins/prp-core/skills|agents`, `.agents/skills`, `.codex/agents`, `profiles/kild/skills`) are **generated** by `scripts/sync_plugin.py` — never hand-edit them; every skill edit below is made in `.claude/skills/` and flowed through `python3 scripts/sync_plugin.py`. Fidelity first: Phases 0–1 preserve behavior modulo the path change; cleanups are deferred to Phase 3.

---

## 1. Target layout under `~/.prp/`

```
~/.prp/                                # root; overridable via $PRP_HOME (PRP-owned env var)
├── MAIN_MEMORY.md                     # cross-project operator memory — created on first write, never pre-created
└── <key>/                             # one per project, e.g. prp-bb91a814
    ├── project.json                   # authoritative registration: {"path": "...", "name": "..."}
    ├── plans/                         #   + plans/completed/ (prp-implement archives here)
    ├── prds/
    ├── research/                      # prp-codebase-question
    ├── research-plans/                # prp-research-team
    ├── reports/                       # prp-implement
    ├── reviews/                       # prp-review (human-readable review reports)
    ├── issues/                        #   + issues/completed/ (prp-issue)
    ├── debug/                         # prp-debug RCA reports
    ├── orchestration/                 # prp-orchestrate run files
    ├── state/                         # runtime state, machine-only:
    │   ├── prp-loop.state.json        #   (+ .tmp during atomic write)
    │   ├── prp-loop.run.log
    │   ├── pr-<N>-cycle-<C>.verdict.json
    │   └── prp-research-team.state    #   Stop-hook sentinel
    └── MEMORY.md · LOG.md · direction.md   # per-project memory — created on first write only
```

### Deviations from the proposed layout, justified

1. **Added `research-plans/`, `reports/`, `issues/`, `debug/`, `orchestration/`** beyond the proposed `plans/ research/ reviews/ prds/` — this preserves the current artifact taxonomy 1:1 (fidelity first; every current `.claude/PRPs/<sub>` maps to the same `<sub>` under the store). Collapsing/renaming dirs is an optimization that can come in Phase 3 if wanted.
2. **Added `state/`** — prp-loop state/log, review verdicts, and the research-team sentinel are *state*, not artifacts. Today they live in-repo and require four `.gitignore` entries plus git-exclude machinery inside `prp_loop.py` (see `LOOP_ARTIFACTS`, `.claude/PRPs/scripts/prp_loop.py:68-72`). Out-of-repo, all of that becomes unnecessary.
3. **No top-level `projects.json`** (deviation from the proposed index). Per-key `project.json` is the source of truth; it has exactly one writer (whoever first touches the store) and no concurrent-write hazard — parallel worktree agents are the whole point of this reshape, and a single shared JSON that every skill appends to is a corruption hazard with no owner. An index is derivable at any time (`cat ~/.prp/*/project.json`), and a future UI can build/cache one itself. This also honors CLAUDE.md's "structure implies a maintainer" — nothing in PRP would keep a global index current. If the human wants `projects.json` anyway, see Open Question 4.
4. **Memory files are never pre-created** — same principle: creating empty `MEMORY.md`/`LOG.md`/`direction.md` that nothing maintains adds stateful structure with no maintainer. Wiring skills to maintain memory is a separate follow-up feature (Open Question 5); this plan only reserves the names/locations.

---

## 2. Project key derivation (exact rule)

The key is a stable slug of the **canonical main-checkout path**, so every worktree of a project resolves to the same store.

1. `gd = git rev-parse --path-format=absolute --git-common-dir` (git ≥ 2.31; this machine has 2.49.0). From any linked worktree this returns the **main checkout's** `.git` dir — verified: in this repo it returns `/Users/rasmus/Projects/mine/sild/prp/.git`.
2. `root`: if `gd` ends with `/.git`, strip that suffix; if the command fails (not a repo), `root = $PWD`; otherwise (bare repo / submodule `.git/modules/...` edge) use `gd` itself.
3. Canonicalize `root` to a **physical path** (`cd "$root" && pwd -P` in shell, `Path(root).resolve()` in Python) — protects against symlinked spellings (`/tmp` vs `/private/tmp`) deriving different keys.
4. `name = slug(basename(root))`: lowercase; every run of chars outside `[a-z0-9]` becomes `-`; trim leading/trailing `-`; if empty, use `project`.
5. `hash8` = first 8 hex chars of the **git blob SHA-1** of the canonical root path string: `printf %s "$root" | git hash-object --stdin | cut -c1-8`. Git is guaranteed present (PRP already requires it), and shelling to the same git command from Python eliminates any shell/Python divergence (never reimplement the blob hash).
6. `key = "<name>-<hash8>"` — for this repo: `prp-bb91a814`.

**Collision handling**: two different canonical paths share a key only on an 8-hex-digit prefix collision *and* an identical basename slug — at single-operator scale, effectively impossible. Defense in depth anyway: `prp_loop.py`'s resolver verifies that an existing `project.json.path` matches the current root and halts on mismatch (a mismatch means either a collision or a different repo now living at a hashed path); the bash convention block stays lean and skips this check (see §3).

**When a repo moves**: the path changes, so the key changes and the project resolves to a fresh, empty store. Recovery is manual and documented (plugin README, §4 file list): `mv ~/.prp/<old-key> ~/.prp/<new-key>` and update `path` in `project.json`. No auto-detection — magic here would need a maintained global index (see deviation 3) and can silently mis-adopt stores. The old store is never deleted by PRP.

**Multiple clones of the same repo** get distinct stores (distinct paths → distinct keys). This is the decided path-based rule; a remote-URL-based key would merge them but breaks for repos with no remote and leaks across forks. Revisit only if it bites (Open Question 1).

---

## 3. Resolution mechanism — recommendation: inline convention block + sync-time drift guard

Skills must stay self-contained (CLAUDE.md "Don't add cross-skill file references", and the meta-skill's self-containment rule), so a single shared resolver script is off the table. The two viable options:

- **(A) Inline convention block**: a ~7-line bash block stated verbatim in each artifact-writing SKILL.md.
- **(B) Bundled resolver script**: a `scripts/prp_home.py` duplicated into every skill's `scripts/` by `sync_plugin.py`.

**Recommendation: (A).** Reasons: the duplication cost of a paragraph is lower than 12 copies of a script; the block runs directly in the harness Bash tool with zero interpreter/uv dependency; it renders harness-neutrally (nothing in it is a Claude-ism, so `CODEX_REWRITES`/`KILD_REWRITES` in `scripts/sync_plugin.py:109-139,249-271` pass it through untouched); and drift — the real risk of duplication — is mechanically eliminated by a new sync-time check (below). (B) would also force `LAUNCHER_REWRITES`-style path juggling (`scripts/sync_plugin.py:77-89`) for 12 more skills across 3 launch contexts.

### The canonical block (verbatim in each artifact-writing skill)

```bash
# --- PRP store resolver (canonical; keep byte-identical across skills) ---
_gd="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"
case "$_gd" in */.git) _root="${_gd%/.git}" ;; "") _root="$PWD" ;; *) _root="$_gd" ;; esac
_root="$(cd "$_root" && pwd -P)"
_name="$(basename "$_root" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-*//;s/-*$//')"
PRP_DIR="${PRP_HOME:-$HOME/.prp}/${_name:-project}-$(printf %s "$_root" | git hash-object --stdin | cut -c1-8)"
mkdir -p "$PRP_DIR"; [ -f "$PRP_DIR/project.json" ] || printf '{"path": "%s", "name": "%s"}\n' "$_root" "${_name:-project}" > "$PRP_DIR/project.json"
```

Notes for the executor:
- `tr -cs 'a-z0-9' '-'` squeezes the trailing newline into a `-` which the `sed` trims — tested behavior, keep the pipeline exactly as written.
- `$PRP_HOME` is PRP's own override (tests, sandboxes). The resolver reads **only** git output, `$PWD`, `$HOME`, `$PRP_HOME` — no other tool's config or env, per the zero-dependency rule.
- Skills then write to `"$PRP_DIR"/plans/`, `"$PRP_DIR"/research/`, etc. (each skill `mkdir -p` its own subdir as today, e.g. replacing `.claude/skills/prp-codebase-question/SKILL.md:206`'s `mkdir -p .claude/PRPs/research`).
- In SKILL.md prose, paths are written as `$PRP_DIR/plans/{name}.plan.md`; reported/echoed paths in final-summary templates must be the **expanded absolute path** (the user can't resolve `$PRP_DIR` mentally — the skill should echo the real one).

### Drift guard in `scripts/sync_plugin.py`

Add a module constant `PRP_RESOLVER_BLOCK` (the exact block above) and a check in `expected_files()` (`scripts/sync_plugin.py:354`): for every source file under `SRC_SKILLS` whose text contains the marker line `# --- PRP store resolver`, the full block must appear byte-identically, else `sys.exit(...)` — same fail-fast pattern as the `CODEX_FORBIDDEN` scan at `scripts/sync_plugin.py:309-311`. This makes the duplicated convention un-driftable: any skill that embeds a stale or edited variant fails `--check` and CI-of-one.

### Python consumers

`prp_loop.py` implements the same rule as `_prp_dir() -> Path`, shelling to the same two git commands (`rev-parse --path-format=absolute --git-common-dir`, `hash-object --stdin`) and using `Path.resolve()` for canonicalization — plus the `project.json.path` mismatch halt described in §2. The loop keeps its separate `_project_root()` (`.claude/PRPs/scripts/prp_loop.py:43-55`, `--show-toplevel`) for *operating* on the checkout — the two notions now differ deliberately: ROOT = the worktree being worked in; PRP_DIR = the per-project store shared by all its worktrees.

---

## 4. Full inventory of current path references

Legend: **[S]** = edit source in `.claude/skills/`, flows to all 4 generated targets via `python3 scripts/sync_plugin.py`. **[H]** = hand-maintained file, edit directly. **[G]** = generated — never edit; listed only so the executor knows the rendered copies exist (e.g. the same lines appear in `plugins/prp-core/skills/...`, `.agents/skills/...`, and for the kild-included skills in `profiles/kild/skills/...` at slightly shifted line numbers because of injected preambles).

### 4.1 Skills — mechanical path swap `.claude/PRPs/<sub>` → `$PRP_DIR/<sub>` + resolver block

Each artifact-writing skill gets the canonical resolver block once (in the step that first writes/reads artifacts), and every listed line swaps the path. Unless noted, the change is purely mechanical.

| File | Lines | Change |
|---|---|---|
| **[S]** `.claude/skills/prp-plan/SKILL.md` | 241, 243, 250 | OUTPUT_PATH / `mkdir -p` / OUTPUT_FILE → `$PRP_DIR/plans/`; add resolver block before 241 |
| **[S]** `.claude/skills/prp-plan/workflows/update-references.md` | 9, 32 | plan-path prose; 32's archive caveat still applies (paths still change on archive) |
| **[S]** `.claude/skills/prp-plan/templates/plan-template.md` | 3 | save-path instruction |
| **[S]** `.claude/skills/prp-plan/templates/report-format.md` | 8, 46 | report file line; 46's next-step `/prp-implement <path>` now shows the absolute store path |
| **[S]** `.claude/skills/prp-prd/SKILL.md` | 216, 218, 385, 418, 453 | prds output path, mkdir, report, next-step `/prp-plan <path>`, ASCII flow diagram |
| **[S]** `.claude/skills/prp-codebase-question/SKILL.md` | 206, 215, 314, 383 | research output; add resolver block at the mkdir (206) |
| **[S]** `.claude/skills/prp-debug/SKILL.md` | 199, 204, 285 | `debug/rca-*.md` output |
| **[S]** `.claude/skills/prp-review/SKILL.md` | 130, 133, 136 | evidence lookup (`ls` of reports / plans/completed / issues/completed) → store paths; **compat**: during the migration window also `ls` the legacy in-repo paths (see §5.3) |
| | 347, 352, 450, 467, 470, 473, 517 | reviews output path, `gh pr review/comment --body-file` args (absolute store paths work fine for `--body-file`) |
| **[S]** `.claude/skills/prp-review/workflows/agents.md` | 122, 125, 132, 181 | same as above for the multi-agent variant |
| **[S]** `.claude/skills/prp-issue/SKILL.md` | 31 | description of investigate — path swap **and behavior change**: drop "commits it" (artifact is out-of-repo; the GitHub comment remains the shared record — Open Question 2) |
| **[S]** `.claude/skills/prp-issue/workflows/investigate.md` | 239, 242, 244, 433, 572 | issues artifact paths |
| | 448 | `git add .claude/PRPs/issues/` — **delete the commit step** (nothing in-repo to commit) |
| **[S]** `.claude/skills/prp-issue/workflows/fix.md` | 52, 79, 413, 574 | artifact lookup/report paths; 52/79 get the legacy-path read-fallback during the window |
| | 525, 526 | archive `mv` → `$PRP_DIR/issues/completed/` |
| | 532 | `git add .claude/PRPs/issues/` — **delete** |
| **[S]** `.claude/skills/prp-implement/SKILL.md` | 296, 301, 426, 465 | reports output |
| | 420, 421, 466 | plan archival `mv $ARGUMENTS $PRP_DIR/plans/completed/` — only when the plan already lives in the store; a plan path given from elsewhere is left in place (note this guard in the text) |
| **[S]** `.claude/skills/prp-research-team/SKILL.md` | 31, 270, 279, 286 | `research-plans/` output |
| | 283 | sentinel write → `$PRP_DIR/state/prp-research-team.state` (must match the hook, see 4.4) |
| **[S]** `.claude/skills/prp-orchestrate/SKILL.md` | 9, 17, 36 | run file → `$PRP_DIR/orchestration/<run-id>.md`; 17's "artifacts under `.claude/PRPs/`" → "artifacts under the project's PRP store" |
| **[S]** `.claude/skills/prp-orchestrate/references/launching.md` | 64 | "under the branch's `.claude/PRPs/`" → "under the project's store — shared across all worktrees, so the orchestrator sees workstream artifacts without merging anything" (this line's per-branch framing described the old broken reality; the reshape is what fixes it) |
| **[S]** `.claude/skills/prp-loop/SKILL.md` | 16, 22, 32 | launcher path → `.claude/skills/prp-loop/scripts/prp_loop.py` (Phase 0 relocation, §4.3) |
| | 9, 51 | state location prose → `~/.prp/<key>/state/prp-loop.state.json` |
| | 41 | "writes `.claude/PRPs/plans/...`" → store path |

**No changes**: `.claude/skills/prp-commit/`, `prp-pr/`, `prp-meta-skill/`, `prp-worktree/` (zero `.claude/PRPs` references — verified by grep). `prp-worktree`'s `.worktrees/` stay in-repo: they are working trees, not artifacts (`.claude/skills/prp-worktree/scripts/worktree.py:7,30`). `.claude/agents/*` — zero references, no changes.

### 4.2 `prp_loop.py` — path port + three latent crashes

Current home `.claude/PRPs/scripts/prp_loop.py` (494 lines); relocates in Phase 0 (§4.3). Line numbers below refer to the current file.

| Lines | Change |
|---|---|
| 15–16, 28–30, 46 | docstring/usage: state location, launcher path, `_project_root` comment |
| new (~57) | add `_prp_dir()` per §3 (shell to git; `project.json` write-if-absent + path-mismatch halt) |
| 59 | `STATE_FILE = ROOT / ".claude" / "prp-loop.state.json"` → `PRP_DIR / "state" / "prp-loop.state.json"` |
| 60 | `PLANS_DIR` → `PRP_DIR / "plans"` |
| 61 | `REVIEW_DIR` → `PRP_DIR / "state"` (verdicts are machine state; prp-review's human-readable reports go to `reviews/` on their own) |
| 68–72 | `LOOP_ARTIFACTS` — keep in Phase 1 (patterns simply never match; harmless), delete in Phase 3 together with `_excludes()`/`_dirty()` plumbing at 209–215 and the `ensure_committed` doc at 218–220 |
| 112 | `STATE_FILE.relative_to(ROOT)` — **ValueError once STATE_FILE is outside ROOT**; → `STATE_FILE` (absolute) |
| 195 | `newest_plan` returns `...relative_to(ROOT)` — same crash; return absolute `str(p)`. Downstream uses (`stage_implement:289`, `stage_fix` prompt) only interpolate the string into prompts — absolute paths are fine and clearer for the stage agents |
| 279 | halt message "no new .plan.md under .claude/PRPs/plans/" → store wording |
| 329 | `rel = verdict_path.relative_to(ROOT)` — same crash; use the absolute path in the prompt (331–335) and messages (340–348) |
| 447 | `STATE_FILE.relative_to(ROOT)` in the "loop exists" error — absolute |
| — | `--resume` compat: old state files carry repo-relative `plan_path` values; the loop only interpolates them into prompts, so tolerate both. If a **legacy** `.claude/prp-loop.state.json` exists in-repo and no store state does, print a one-line hint ("legacy loop state found at ...; finish it with the previous version or move it to <store>/state/") and exit — no auto-migration (Open Question 6) |

### 4.3 `scripts/sync_plugin.py` — relocation + drift guard

**Phase 0 decision: move the loop script source** from `.claude/PRPs/scripts/prp_loop.py` to `.claude/skills/prp-loop/scripts/prp_loop.py`. Rationale: `.claude/PRPs/` must cease to exist in every repo including this one; the script is intelligence, not artifact; and the move *deletes* sync special-cases rather than adding any (the generic skill-tree walk picks it up). `prp-worktree` already models this shape (`scripts/sync_plugin.py:84-88`).

| Lines | Change |
|---|---|
| 10 | docstring: bundling note becomes obsolete — the script now lives inside the skill |
| 52 | `SRC_LOOP_SCRIPT` — delete the constant |
| 79–83 | `LAUNCHER_REWRITES["prp-loop"]` local path → `.claude/skills/prp-loop/scripts/prp_loop.py` (plugin/codex sides unchanged) |
| 131–132 | the codex rewrite `\.claude/PRPs/scripts/prp_loop\.py` → drop the entry; the general `.claude/skills/` → `.agents/skills/` map at 136 now covers it (`LAUNCHER_REWRITES` already rewrote SKILL.md before `codex_render_md` runs, so 136 is belt-and-braces for prose mentions) |
| 370 | `expected[PLUGIN_SKILLS / "prp-loop/scripts/prp_loop.py"] = SRC_LOOP_SCRIPT.read_bytes()` — delete (generic walk at 359–369 covers it) |
| 392 | same deletion for the codex render (walk at 377–391 covers it; `.py` files copy verbatim per 390–391) |
| new | `PRP_RESOLVER_BLOCK` constant + verbatim check per §3 |
| — | no new `CODEX_REWRITES`/`KILD_REWRITES` needed for store paths: `$PRP_DIR` / `~/.prp` contain no Claude-isms, and `CODEX_FORBIDDEN`/`KILD_FORBIDDEN` (207–212, 273) are unaffected. The kild profile (`KILD_INCLUDED_SKILLS`, 221–229) picks the new paths up on regeneration; `KILD_LANE_NOTE` (231–240) still correctly forbids archival moves — now they'd be store-side `mv`s, still the driver's job |

### 4.4 Hand-maintained plugin + docs + repo config

| File | Lines | Change |
|---|---|---|
| **[H]** `plugins/prp-core/hooks/prp-research-team-stop.sh` | 13 | `SENTINEL_FILE=".claude/prp-research-team.state"` → inline the §3 resolver (it's bash; hooks run with cwd = the project) and read `$PRP_DIR/state/prp-research-team.state`. The rest of the script (mtime staleness at 23–28, output-path validation at 33–40) works unchanged with absolute paths — the sentinel's first line will now contain an absolute output path |
| **[H]** `plugins/prp-core/README.md` | 88, 90, 99 | example invocations with plan/prd paths |
| | 161–175 | "Artifacts" section: rewrite to the `~/.prp/<key>/` layout, the key rule, `$PRP_HOME`, and the repo-move recovery note (§2) |
| **[H]** `README.md` | 131, 164 | prp-loop state location |
| | 139, 177, 181, 195 | pipeline/example paths |
| | 214–225 | "Artifacts Structure" section → `~/.prp/<key>/` layout |
| | 263 | project-structure diagram: drop the `PRPs/` line under `.claude/` |
| **[H]** `CLAUDE.md` | 29 | launcher-path prose `(.claude/PRPs/scripts/prp_loop.py → ...)` → new source location; simplify since bundling special-case is gone. Add one "What lives where" bullet for `~/.prp/<key>/` (artifacts/state live out-of-repo; resolver convention in the skills) |
| **[H]** `.gitignore` | 16–18 | `.claude/prp-loop.state.json`, `.run.log` — obsolete after migration; remove in Phase 2 |
| | 20–21 | `.claude/PRPs/reviews/*.verdict.json` — same |
| | 23–24 | `.claude/prp-research-team.state` — same |
| | 26–30 | `.worktrees/`, `.claude/worktrees/` — **keep** (working trees, unrelated) |
| **[H]** `CONTRIBUTING.md` | 21 | only mentions `old-prp-commands/` historical `PRPs/` — no change |

**Untouched by policy**: `old-prp-commands/` (CLAUDE.md:33,53 — reference only; its `PRPs/templates` mentions describe the retired generation). `claude_md_files/` — grep-verified clean.

**[G] Generated copies** (regenerate, never edit): `plugins/prp-core/skills/**` (e.g. `prp-plan/SKILL.md:241,243,250`), `plugins/prp-core/agents/**`, `.agents/skills/**`, `.codex/agents/**`, `profiles/kild/skills/**` (e.g. `prp-plan/SKILL.md:244,246,253` — kild line numbers shift by the injected lane preamble). After Phase 0/1 edits, one `python3 scripts/sync_plugin.py` run rewrites all of them; `--check` proves it.

### 4.5 This repo's own store content (migration input)

Tracked (must `git rm` in the migration commit): `.claude/PRPs/features/completed/add-prp-core-runner-skill.md`, `.claude/PRPs/issues/completed/issue-11.md`, `.claude/PRPs/orchestration/2026-07-15-backlog-batch.md`, `.claude/PRPs/plans/completed/consolidate-prp-skills.plan.md`, `.claude/PRPs/reports/consolidate-prp-skills-report.md`, `.claude/PRPs/scripts/prp_loop.py` (relocated in Phase 0, not migrated). Untracked (plain `mv`): `.claude/PRPs/research/*` (7 files incl. `.mmd`/`.svg`), this plan (`.claude/PRPs/plans/prp-home-reshape.md` — migrate it too once executed), `.claude/PRPs/scripts/__pycache__/` (delete). `features/` has no owning skill anymore (legacy dir) — migrate it under `<key>/features/` as-is rather than dropping content.

---

## 5. Migration

### 5.1 What stays in a consuming repo: nothing PRP-specific

Justification: the resolver derives the store from git alone, so no in-repo marker/pointer file is needed — and any in-repo file would resurrect both original bugs (unwritable in repos the user doesn't control; invisible in worktrees when gitignored). What remains in-repo is not PRP's: the harness config (`.claude/settings*`, hooks), `CLAUDE.md`, and `prp-worktree`'s `.worktrees/` working trees. Consuming projects that vendored the skills keep them (skills are intelligence, distributed via the plugin or `.claude/skills/` — unchanged by this plan).

### 5.2 Per-project migration procedure

Ship `scripts/migrate_prp_home.py` in this repo (operator tool, NOT bundled into any skill — it's one-time tooling, and bundling would bloat 12 skills for a single-use script). Location-agnostic per CLAUDE.md rule 4 (derive the project from cwd/git, never `__file__`). Behavior, runnable per project as `python3 <prp-repo>/scripts/migrate_prp_home.py [--dry-run]`:

1. Compute `root`/`key` exactly per §2 (shell to git; refuse to run from a linked worktree unless `--force`, to keep `git rm` on the main checkout).
2. `mkdir -p ~/.prp/<key>`; write `project.json` if absent (halt on path mismatch).
3. Move every existing `.claude/PRPs/<sub>/` (plans incl. `completed/`, prds, research, research-plans, reports, reviews, issues incl. `completed/`, debug, orchestration, features) to `~/.prp/<key>/<sub>/`, merging into existing dirs, never overwriting a same-named file (suffix `.migrated` on conflict and report it).
4. Move legacy state if present: `.claude/prp-loop.state.json` → `state/`, `.claude/prp-loop.run.log` → `state/`, `.claude/prp-research-team.state` → `state/`.
5. If the moved files were tracked: `git rm -r --cached .claude/PRPs` (and the state files) and print the suggested commit command — the script itself never commits (CLAUDE.md: commit only when asked). For repos the user doesn't control, everything is untracked/ignored and steps land as plain filesystem moves.
6. Remove the now-empty `.claude/PRPs/`; print which `.gitignore` lines are now dead (matching §4.4) without editing them.

Also migrate ai_docs where present: consuming projects that still carry `PRPs/ai_docs/` from the old command generation are out of scope (that generation is retired; `old-prp-commands/` stays as-is), but the script should *report* such dirs if seen, not touch them.

### 5.3 Backward-compat window

- **Writes: new location only, from day one.** No dual-writes — one source of truth (CLAUDE.md principle); a dual-write window doubles drift for zero benefit since the migration script exists.
- **Reads: two fallbacks only**, where a skill consumes *pre-existing* artifacts: `prp-issue` fix's artifact lookup (`workflows/fix.md:52,79`) and `prp-review`'s evidence gathering (`SKILL.md:130-136`) also check the legacy `.claude/PRPs/...` path and, on a hit, tell the user to run the migration script. `prp-implement` needs none (the plan path is an explicit argument). `prp-loop --resume` gets the hint-and-exit described in §4.2.
- **Window**: until the operator's active projects are migrated — recommend ~2 weeks of daily use, then Phase 3 removes the fallbacks. Removal is a grep for the legacy path plus regeneration; the drift guard doesn't cover fallback prose, so the Phase 3 gate greps `-r '\.claude/PRPs' .claude/skills` expecting zero hits.

---

## 6. Phasing and validation gates

Each phase is its own feature branch + PR (`development` base), conventional commits, no AI attribution. Fidelity first: 0 and 1 preserve behavior (modulo the store location itself), 2 migrates data, 3 optimizes.

### Phase 0 — relocate `prp_loop.py` into the skill (zero behavior change)

`git mv .claude/PRPs/scripts/prp_loop.py .claude/skills/prp-loop/scripts/prp_loop.py`; sync edits per §4.3 (lines 10, 52, 79–83, 131–132, 370, 392); `prp-loop/SKILL.md:16,22,32`; `CLAUDE.md:29`; delete `.claude/PRPs/scripts/__pycache__/`.

Gates:
1. `python3 -m py_compile .claude/skills/prp-loop/scripts/prp_loop.py`
2. `python3 scripts/sync_plugin.py && python3 scripts/sync_plugin.py --check` → "all targets in sync"; `git diff --stat` over `plugins/ .agents/ .codex/ profiles/` shows only the expected launcher-path lines and the (unchanged-content) script arriving via the walk
3. `uv run .claude/skills/prp-loop/scripts/prp_loop.py --resume` → exits "no state file to resume from" (proves the launcher path and imports)
4. `grep -rn '\.claude/PRPs/scripts' .claude/ scripts/ plugins/ .agents/ profiles/ README.md CLAUDE.md` → zero hits

### Phase 1 — resolver + store port (the behavior-preserving path swap)

Resolver block + drift guard (§3); all skill edits (§4.1); `prp_loop.py` port incl. the three `relative_to` crashes (§4.2); hook script (§4.4); read-fallbacks (§5.3); regenerate.

Gates:
1. `python3 -m py_compile .claude/skills/prp-loop/scripts/prp_loop.py`
2. `python3 scripts/sync_plugin.py --check` (now also proving resolver-block verbatim-ness; deliberately corrupt one copy → `--check` must fail, then restore)
3. Resolver determinism: run the block in this repo and in a throwaway worktree (`git worktree add /tmp/prp-wt && cd /tmp/prp-wt`) → identical `PRP_DIR`; `git worktree remove`
4. `grep -rn '\.claude/PRPs' .claude/skills` → hits only in the two documented read-fallbacks
5. **End-to-end skill exercise** (the real test per CLAUDE.md): in a scratch repo with `PRP_HOME=$(mktemp -d)`, (a) trigger `prp-codebase-question` on a trivial question → artifact lands in `$PRP_HOME/<key>/research/` and the repo tree stays clean (`git status` empty); (b) `uv run .../prp_loop.py "tiny feature" --until plan` → plan in `$PRP_HOME/<key>/plans/`, state in `$PRP_HOME/<key>/state/prp-loop.state.json`, nothing under `.claude/`
6. Hook: touch a fake sentinel in the store, run the Stop-hook script with stub stdin → validates/cleans up against store paths

### Phase 2 — migration

`scripts/migrate_prp_home.py` (§5.2); run it on this repo (migrating §4.5 content, `git rm` of tracked artifacts in a dedicated commit); run on the operator's active projects; `.gitignore` cleanup (§4.4); `README.md` + `plugins/prp-core/README.md` rewrites (§4.4).

Gates:
1. `python3 -m py_compile scripts/migrate_prp_home.py`; `--dry-run` on a fixture repo (tracked + untracked + conflicting files) matches the promised moves exactly
2. After migrating this repo: `test ! -d .claude/PRPs`; `git status` clean post-commit; `ls ~/.prp/prp-bb91a814/` shows the migrated taxonomy
3. `python3 scripts/sync_plugin.py --check` still green (docs edits touch no generated files)
4. Re-run one skill (`prp-review` evidence step or `prp-issue` fix lookup) in a migrated project → finds migrated artifacts at the new location, no legacy-path warning

### Phase 3 — optimize (only after the window)

Remove read-fallbacks (§5.3); delete `LOOP_ARTIFACTS`/`_excludes()`/`_dirty()` exclude plumbing (`prp_loop.py:68-72,209-215`) and simplify `ensure_committed` (218–231); optionally collapse artifact taxonomy; memory-file wiring goes to its own plan.

Gates: `py_compile`; `sync --check`; `grep -rn '\.claude/PRPs' .` → hits only in `old-prp-commands/` and git history; one full `prp-loop --until implement` run in a scratch repo (proving `ensure_committed` still never sweeps store files — trivially true, they're out-of-repo).

---

## 7. Open questions for the human (with recommendations)

1. **Multiple clones of one repo = multiple stores.** Path-based keying (decided) gives each clone its own store. Accept, or key by remote URL to share? **Recommendation: accept path-based**; URL keying breaks remote-less repos and merges forks that shouldn't merge. Revisit only if it actually bites.
2. **`prp-issue` stops committing investigation artifacts** (`investigate.md:448`, `fix.md:532` deleted). The GitHub issue comment remains the shared/team-visible record; the store copy is personal. OK to drop the commits? **Recommendation: yes** — committing personal artifacts into consuming repos is exactly what this reshape ends.
3. **Compat-window length** for the two read-fallbacks and the `--resume` hint. **Recommendation: ~2 weeks of daily use across your active projects, then Phase 3 removes them.**
4. **Top-level `~/.prp/projects.json`**: the plan drops it in favor of per-key `project.json` (deviation 3, §1) — concurrency-safe and maintainer-free; an index is a `cat ~/.prp/*/project.json` away. Keep it dropped, or is a maintained global index wanted now (and if so, who owns writes)? **Recommendation: dropped; let a future UI own any index it needs.**
5. **Memory files** (`MAIN_MEMORY.md`, `<key>/MEMORY.md`, `LOG.md`, `direction.md`): locations reserved, nothing creates or maintains them yet. Wiring skills to read/write memory is a separate feature plan. **Recommendation: defer; create-on-first-write only, never scaffold empties.**
6. **Legacy `prp-loop` state**: hint-and-exit (recommended) vs auto-migrating an in-flight loop's state file. **Recommendation: hint only** — in-flight loops are short-lived; auto-migration code would outlive its usefulness within days.
7. **Review verdicts under `state/`** (machine JSON, per §4.2 line 61) while human-readable reviews go to `reviews/`. Any objection to splitting them? **Recommendation: split as planned** — verdicts were already gitignored machine state (`.gitignore:21`).

---

## Appendix A — grep basis

Inventory produced from: `grep -rn '\.claude/PRPs' .claude/skills scripts profiles plugins .agents .codex claude_md_files README.md CLAUDE.md CONTRIBUTING.md .gitignore`, plus targeted greps for `prp-loop.state`, `run.log`, `prp-research-team.state`, `research-plans`, and `git ls-files .claude/PRPs`. Key derivation verified live: `git rev-parse --path-format=absolute --git-common-dir` → `/Users/rasmus/Projects/mine/sild/prp/.git`; `printf %s "/Users/rasmus/Projects/mine/sild/prp" | git hash-object --stdin | cut -c1-8` → `bb91a814` (git 2.49.0).

## Appendix B — optional integrations (owned by the integrating layer, NOT PRP)

An orchestrating layer or UI that happens to drive both PRP and a generic engine with a configurable memory/artifact directory may point that engine's directory at the same per-project store (e.g. writing the engine's `memory.dir` config to `~/.prp/<key>` in a project it manages) so both layers share one store. That wiring belongs entirely to the integrating layer: PRP core never reads or writes any other tool's config or environment, and the `~/.prp` resolver depends only on git, `$PWD`, `$HOME`, and `$PRP_HOME`.
