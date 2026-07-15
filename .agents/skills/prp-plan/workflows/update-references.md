# Update Plan References

> **Arguments:** `$ARGUMENTS` (and `$1`, `$2`, ...) refer to the arguments given when this skill was invoked. Take them from the user's request; if absent, infer them from the conversation.

Wire bidirectional back/forward references between PRP plan files — the `## Lifecycle` section's **Back refs** / **Forward refs**. Keep both sides in sync so the plan graph stays navigable for the whole team and for agents.

This is the `update-references` workflow of `prp-plan`. Invoke it when the request is to **link/connect two existing plans** rather than to create a new plan.

## Variables

PLAN: $1 — the plan to update (path under `.claude/PRPs/plans/`)
RELATED: $2 — the related plan/doc to link
DIRECTION: $3 — `back` (PLAN builds on / depends on RELATED) or `forward` (RELATED builds on / extends PLAN); infer from the prompt if omitted

## Instructions

- If `PLAN` or `RELATED` is missing, stop and ask for both.
- Only operate on plans that have a `## Lifecycle (append-only)` section. If a target lacks one, tell the user and stop (bring it onto the current `prp-plan` template first).
- All reference edits are append-only: add links, never remove or overwrite existing ones, and never duplicate a link already present.

## Workflow

1. **Locate the plans** — Resolve `PLAN` and `RELATED` to files; confirm both exist and have a `## Lifecycle` section.
2. **Determine direction** — From `DIRECTION` or the prompt: `back` = PLAN depends on / builds on RELATED; `forward` = RELATED builds on / extends PLAN. The reciprocal is always the opposite — a back ref on one side is a forward ref on the other.
3. **Update PLAN** — In PLAN's Lifecycle, append the link to **Back refs** (if `back`) or **Forward refs** (if `forward`): a repo-relative path to RELATED plus a short label. Skip if already present.
4. **Update RELATED (reciprocal)** — In RELATED's Lifecycle, append the opposite-direction link back to PLAN (repo-relative path + label). Skip if already present.
5. **Stamp both** — Append the current ISO-8601 timestamp to **Modified** on every plan touched (append-only).
6. **Record amendments** — Append one `## Amendments` entry (newest at bottom) to each plan touched, noting the reference added and its direction.
7. **Report** — List each plan touched and the references added in each direction.

## Notes

- Use repo-relative paths so links survive moves within the repo.
- Caveat: if `prp-implement` archives a plan to `.claude/PRPs/plans/completed/`, its path changes and existing refs go stale. For plans you expect to archive, re-run this workflow after archiving (or link by a stable identifier).
