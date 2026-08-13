---
name: prp-loop
description: Runs the detached, resumable PRP pipeline in fresh headless CLI sessions, cycling plan, implementation, PR, review, and corrections with persisted state and safety bounds. Use only when the user explicitly asks to "run the full PRP loop", "run this detached", "continue across context windows", use headless autonomous execution, resume a saved loop, or invokes /prp-loop. Use prp-issue for ordinary end-to-end delivery.
argument-hint: "<feature description> [--base <branch>] [--max-cycles N] [--validate \"<cmd>\"] | --resume"
---

# PRP Loop — autonomous cyclic pipeline

Launch the orchestrator that drives `plan → implement (commit + PR) → review` and loops `review → fix` until the PR review is clean (or limits are hit). It runs headless `claude -p` once per stage and tracks progress in `~/.prp/<key>/state/prp-loop.state.json`.

## Run it

Start a new loop with the user's request as the feature argument:

```bash
uv run .claude/skills/prp-loop/scripts/prp_loop.py "$ARGUMENTS"
```

Resume a halted or in-progress loop:

```bash
uv run .claude/skills/prp-loop/scripts/prp_loop.py --resume
```

Defaults: `--max-cycles 3`, `--max-implement-iterations 10`, base branch auto-detected. Pass `--validate "<cmd>"` to give the loop an authoritative green check (exit 0 = pass).

### Stop after a stage (`--until`)

Pass `--until <stage>` (`plan` | `implement` | `pr` | `review` | `fix`) to halt once that stage completes:

```bash
uv run .claude/skills/prp-loop/scripts/prp_loop.py "$ARGUMENTS" --until implement
```

`--until implement` runs `plan → implement` and stops once validations are green and the implementation skill has committed and opened its PR — **no review**.

**UX note:** the retired Ralph loop was single-session and interactive (a Stop-hook fed the prompt back in the same session). `prp-loop --until implement` is headless instead — it drives fresh `claude -p` sessions per iteration and you resume/inspect via the state file rather than watching it live.

## What it does

1. **plan** — `prp-plan` writes the plan under the project's PRP store at `$PRP_DIR/plans/<feature>.plan.md`.
2. **implement** — `prp-implement` executes and validates the plan, commits the work, and opens the PR (bounded by `--max-implement-iterations`).
3. **pr compatibility** — if an older implementation run did not open a PR, `prp-pr` does so once.
4. **review** — `prp-review` runs its default code and seam reviewers, writes the canonical report, and publishes that complete report to GitHub.
5. **cycle** — if the verdict needs fixes, the complete report, plan, and live PR feed into a fresh `prp-implement` correction pass → push → re-review, up to `--max-cycles`. Ready to merge → done; review incomplete → halt.

## Safety

- Fully autonomous (`--dangerously-skip-permissions`). Operates only on the feature branch — it refuses to PR from `main`/`master`/`development`/the base branch.
- Halts with state preserved on: implement/fix not green after the iteration limit, review still dirty after `--max-cycles`, a fix pass with no new commit (no progress), failed push, or any stage error.
- Inspect or resume via `~/.prp/<key>/state/prp-loop.state.json`.

## Notes

This orchestrator is self-contained and uses **no** Stop-hook. It owns both loops itself and detects "green" from each stage's `VALIDATION: GREEN` sentinel (or the `--validate` command). The PRP skills it calls are invoked verbatim and never modified.
