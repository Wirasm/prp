# Launch, steer, and verify workstreams

Use native background agents. Never construct detached CLI processes here.

## Resolve capacity

Keep the run's configured `max-parallel` at the user's value or `10`. Count active delivery owners,
not their nested review agents. Reserve enough harness capacity for the root, each active delivery
owner, one fresh stage coordinator per delivery, and one sequential leaf specialist per coordinator.

When total harness capacity is known, use:

```text
effective delivery owners = min(configured max-parallel, floor((capacity - 1) / 3))
```

Require capacity of at least four for one delivery. When capacity is unknown, launch one delivery
owner and keep the configured value unchanged. Dependencies, overlap, or a rejected spawn can lower
actual concurrency without changing the configured maximum. Retry queued work when a slot frees.

## Prepare the exact checkout

Fetch before launching and verify that the confirmed `origin/<base>` exists. Every workstream that
touches the checkout starts from that exact ref. Never substitute the remote default or a divergent
local branch.

Spawn via the Agent/Task tool:

**A checkout's lifetime belongs to its workstream, not to the agent holding it.** Owners are resumed
between phases as a matter of course, so create the checkout before launching and keep it until the
workstream is merged or dropped:

```text
/prp-worktree create <branch> --base <base>
```

Pass the absolute path it prints to the owner. Before editing, require the owner to verify or create
`<branch>` from `origin/<base>`. If an existing branch has work, preserve it and verify its intended
base rather than resetting it.

Do not use the Agent tool's `isolation: "worktree"` for a workstream that may be resumed. The harness
reclaims that checkout once it releases an unchanged owner, which is what a finished delivery looks
like, and the next resume lands silently in the operator's own checkout.

- Give PR-producing work one agent, `run_in_background` (the default), in its own managed worktree.
- Give `prp-review` a managed worktree because it runs `gh pr checkout`.
- Run work that does not modify the checkout as a plain background agent: `prp-codebase-question`,
  `prp-debug`, `prp-plan`, and `prp-prd`. Assign only one `prp-debug` owner per GitHub issue because it
  can publish there.
- Follow a repository's managed-worktree convention when one exists.
- Keep the raw agent handle in the live session for follow-up messages, stop, and status. Write
  only the run-local alias to the run file, plus a PID for a process-backed integration.

## Construct the owner prompt

A background owner receives no conversation history. Pass the source and only the context needed to
preserve the operator's meaning:

- For checkout-bearing work, add `Work in <absolute worktree path> on <branch>, created from origin/<base>.`
- For PR-producing work, add `Open the PR against <base>.`
- Omit both instructions when they do not apply.

```text
Run the <prp-skill> skill against <source or complete natural-language request>.

Relevant operator context:
<context or decisions that materially affect this workstream; omit when none>

Continue until the selected skill reaches its own definition of done. Return its promised artifact and
proof. If progress requires a decision only the operator can make, return the exact decision needed
with the recommendation.
```

## Steer and report status

- **Steer or continue**: send the owner a follow-up message. Preserve its context for corrections and
  conflict resolution. A resumed owner may no longer hold the checkout it had, and a lost one silently
  becomes the operator's. Restate its absolute worktree path in every follow-up and require
  `git rev-parse --show-toplevel` to confirm it before any git command. Recreate the worktree when it
  is gone rather than letting the owner work wherever it landed.
- **Stop**: use the native stop control. Record `dropped` and the reason. Preserve the worktree and
  branch unless later cleanup proves deletion safe.
- **Status**: reconcile native task status, the run row, and GitHub. Return a compact outcome table and
  put blockers or decisions at the end. Do not forward raw agent narration.

## Verify completion

Treat the owner's final message as an artifact map. Verify the real state before changing the run row:

```bash
gh pr view <number> --json number,url,isDraft,state,baseRefName,headRefName,headRefOid
gh pr checks <number> --required
git log --oneline origin/<base>..origin/<branch> | head -3
git diff --name-only origin/<base>...origin/<branch>
```

For a delivery, read the canonical review report and require:

- an open, non-draft PR targeting the confirmed base;
- a verified published `READY TO MERGE` verdict;
- `reviewed_head` equal to the current `headRefOid`;
- every finding in a terminal disposition;
- every required check green for the current PR head.

When no required CI exists, run the repository's authoritative local gate against the branch. Capture
each command's own exit code. Do not treat a piped pager's exit code as the gate result. Optional checks
remain evidence but do not block the terminal state.

Use the three-dot merge-base diff for PR scope. Verify every plan, implementation report, review report,
publication URL, or spike report promised by the engine under the shared PRP store.

## Clean up after each merge

After GitHub reports the PR merged, fetch and verify its merge commit is reachable from
`origin/<base>`. Read the PR's `headRefOid`, release its owner, and remove the checkout before deleting
branches. Preserve dirty worktrees, changed refs, or a checkout still owned by a live agent.

Use `git worktree list` to choose teardown. A worktree under `.worktrees/` belongs to `prp-worktree`
and needs explicit teardown. For any other path, release the native owner and verify the harness removed
the unchanged checkout. For a managed worktree, invoke:

```text
/prp-worktree remove <branch>
```

After no worktree holds the branch, compare and delete the exact reviewed refs:

```bash
git update-ref -d refs/heads/<branch> <headRefOid>
git push --force-with-lease=refs/heads/<branch>:<headRefOid> origin --delete <branch>
```

A stale-ref rejection means another actor changed the branch. Preserve it and report the remaining
cleanup in the final handoff. This exact-identity path supports merge, squash, and rebase merges without
weakening `prp-worktree`'s ancestry checks.
