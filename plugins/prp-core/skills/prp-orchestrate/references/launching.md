# Launching & Monitoring Workstreams

Mechanics for Lane B (detached headless sessions in worktrees) and Lane A (in-session subagents). All commands run from the orchestrator session.

## Worktree setup (Lane B)

One worktree + one branch per workstream, as siblings of the main checkout so globs and tooling inside the repo never see them:

```bash
REPO_ROOT=$(git rev-parse --show-toplevel)
REPO_NAME=$(basename "$REPO_ROOT")
SLUG=<workstream-slug>                      # e.g. issue-123, auth-phase-2
BRANCH=<branch-name>                        # e.g. fix/issue-123, feat/auth-phase-2
WT="$REPO_ROOT/../$REPO_NAME--$SLUG"

git -C "$REPO_ROOT" worktree add -b "$BRANCH" "$WT" <base-branch>
```

- Base each workstream on the integration branch (usually `development` or `main`), not on another workstream, unless a dependency edge demands stacking.
- If the project needs per-checkout setup (env files, install), do it now — headless sessions won't stop to ask.

## Launch command (Lane B, Claude Code)

Launch from *inside the worktree* so the session's project root, skills, and artifacts are the worktree's own:

```bash
LOG="$WT/.claude/orchestrator-ws.log"
cd "$WT" && nohup claude -p "<workstream prompt>" \
  --dangerously-skip-permissions \
  --output-format stream-json --verbose \
  > "$LOG" 2>&1 &
echo $!   # record this PID in the run file
```

- `stream-json` + `--verbose` makes the log tail-able for liveness; the final line carries the result object.
- `--dangerously-skip-permissions` is what makes the session autonomous — this is why Lane B is reserved for work the user approved at the Phase-1 gate.
- Prefer the harness's background-task facility (e.g. `run_in_background` Bash) over raw `nohup` when available — completion is then signalled instead of polled.
- `.claude/orchestrator-ws.log` is per-worktree state; ensure it is not committed (add to `.gitignore` if the project doesn't already ignore it — check before the workstream's first commit sweeps it in).

## Workstream prompt shape

A headless session inherits nothing from the orchestrator's conversation. The prompt must carry everything:

```
Use the <prp-skill> skill to <task, one line>.

Context:
- Target: <issue #N / plan path / feature description>
- Base branch: <base>. Work only on the current branch (<branch>); never switch or push to <base>.
- Standing decisions that apply to you: <the SD entries scoped to this workstream, verbatim>

Definition of done: <PR opened against <base> with validations green / plan file written / report written>.
If blocked on a decision only a human can make, open the PR as a draft, describe the
blocker in the PR body, and stop.
```

The "if blocked" clause is the workstream's escalation path — a draft PR with a described blocker is an authoritative, monitorable signal (unlike words in a log).

## Engines per workstream type

| Workstream | Prompt core |
|---|---|
| GitHub issue | `Use the prp-issue skill: first investigate #N, then fix #N.` |
| Feature, plan exists | `Use the prp-implement skill to execute the plan at <path>, then use the prp-pr skill to open a PR.` |
| Feature, autonomous | `Use the prp-loop skill for: <feature description>.` (the loop handles plan→implement→pr→review itself; the orchestrator then only gates the final merge) |
| Plan only (staged) | `Use the prp-plan skill to create an implementation plan for: <feature>.` — orchestrator gates the plan, then relaunches with prp-implement |

## Lane A — in-session subagents (Claude Code only)

For read-only fan-out (parallel reviews, research, triage): launch subagents via the Task/Agent tool, all in a single message so they run concurrently. Use the pack's advisory agents (`prp-core:code-reviewer`, `prp-core:codebase-analyst`, …) or have a general agent run a read-only skill by name. Constraints: no commits, no pushes, no worktrees needed; results come back as the agent's report, which the orchestrator digests into the run file.

## Monitoring commands

```bash
gh pr list --head <branch> --json number,url,isDraft,state   # authoritative: PR exists / draft-blocked
gh pr checks <number>                                        # authoritative: CI state
git -C "$WT" log --oneline -3                                # progress: new commits
for d in plans reports reviews issues; do                    # progress: new artifacts
  ls -t "$WT/.claude/PRPs/$d" 2>/dev/null | head -3
done
kill -0 <PID> 2>/dev/null && echo alive || echo dead          # liveness
tail -5 "$LOG"                                                # liveness/debug only — never status truth
```

A **draft PR** from a workstream means "blocked, needs a human decision" (per the prompt shape) — treat it as a gate, read the PR body for the blocker.

## Restarting a stalled/failed workstream

The worktree and branch survive the session — restart with corrective feedback, same launch command, new prompt:

```
Continue the work on the current branch. Previous attempt: <what the log/PR shows>.
Problem: <the stall/failure>. <Corrective instruction.>
<Original definition of done.>
```

Record the restart in the Event Log. Two failed restarts → stop restarting, raise at a gate.

## Cleanup (Phase 7 only)

```bash
git -C "$REPO_ROOT" branch --merged <base> | grep <branch>   # verify merged FIRST
git -C "$REPO_ROOT" worktree remove "$WT"                    # refuses if dirty — good; investigate before --force
git -C "$REPO_ROOT" branch -d "$BRANCH"                      # -d not -D: refuses unmerged
```

## Per-harness notes

- **Claude Code**: everything above works as written. Skills resolve inside worktrees from the checked-in `.claude/skills/` or the globally installed prp-core plugin.
- **Other harnesses (Codex CLI, etc.)**: the protocol core is identical — worktree per workstream, headless CLI invocation, artifacts + PR state as the only truth, run file in the main checkout. Replace the launch command with the harness's headless equivalent and its permission flags. Two degradations: Lane A may not exist (do read-only fan-out as Lane B sessions or sequentially), and PRP skills may not auto-load from `.claude/skills/` — inline the skill's instructions into the prompt, or port the skills to the harness's format first.
