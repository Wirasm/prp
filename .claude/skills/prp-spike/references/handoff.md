# Handoff

Two questions at the end of a spike: where the evidence lives so someone else can follow it, and where the verdict goes so it changes something.

## Making the evidence followable

`$PRP_DIR` is **local-only**. A path into it is unfollowable by anyone but the operator — so the moment a verdict travels to a shared surface, a store pointer stops being evidence and becomes a claim.

| Route | When | Cost |
|---|---|---|
| **Store** — `$PRP_DIR/spikes/<slug>/` | Always. The operator's permanent copy, shared across the project's worktrees, survives a discarded checkout | none |
| **Gist** | The verdict is going somewhere other people read — an issue, a ticket, a review thread | one command, nothing enters the repo |
| **Branch** | The spike code is substantial and worth re-running in-repo | a branch to maintain; only if it carries a commit |

These compose — the store copy always exists; a gist or branch is added when the verdict needs to travel.

**Under `--here` there is no branch at all.** Capture the work as `git diff > "$PRP_DIR/spikes/spike-<slug>.patch"` (add `git diff --cached` and any untracked files if either exists), restore the checkout to the state it was found in, and point Evidence at the patch.

**Gist mechanics.** Push the report *and* the artifacts the verdict rests on, so the link is self-contained:

```bash
gh gist create --secret \
  -d "<project> spike evidence: <slug> (<YYYY-MM-DD>)" \
  "$PRP_DIR/spikes/spike-<slug>.md" "$PRP_DIR/spikes/<slug>"/*
```

- **Secret, not public.** Unlisted but linkable is the right default for throwaway evidence, especially against a private repo. Secret gists are still readable by anyone with the URL — never push credentials, internal hostnames, or customer data. Read what is being pushed first.
- **Create the gist before writing the issue or comment**, so the URL exists when the body is composed.
- Record the URL in the report's Evidence field alongside the store path. The store copy stays authoritative; the gist is a snapshot and does not update itself.

## Routing the verdict

A spike that ends in the operator's terminal changes nothing. Propose where it should land, then **stop and let the operator decide** — creating or commenting on a tracker item is outward-facing, and a spike's terminal act is a verdict, never a merge or a PR.

The input tells you the destination:

| Input the spike started from | Propose |
|---|---|
| An issue / ticket reference | A comment on it carrying the verdict, the deciding evidence, and the gist link. The spike was commissioned by that thread; the answer belongs there |
| Free text, no reference | Search the tracker for a related item first (`gh issue list --search`). Propose commenting on the closest match, or a new issue when nothing fits — say which, and why |
| A plan or PRD step | The plan's own artifact, plus whatever tracks that work |

Then let the verdict shape what gets proposed:

- **PROVEN** — the finding unblocks work. Propose the ticket that work needs, and say plainly which parts the spike did *not* touch, so the estimate is not read off a throwaway build.
- **DISPROVEN** — a path is closed. This belongs wherever the path was proposed, or it gets re-proposed by the next person. Lead with the wall it hit.
- **CONDITIONAL** — the constraint is the deliverable, and it needs a decision-maker, not a filing cabinet. Propose an item that states the trade — what changes, blast radius, what else it unlocks — and frame it as a decision rather than a task. A CONDITIONAL verdict filed as a to-do quietly becomes someone's chore instead of the choice it actually is.

Always offer the option of doing nothing. A spike that closed a question and needs no downstream work is a complete result, and manufacturing a ticket for it is noise.
