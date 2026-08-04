---
name: prp-worklist
description: Render the open work of a repository as something worth looking at, so the maintainer can see what to take next. Deliberate invocation only — /prp-worklist.
argument-hint: "[repo] — defaults to the current repository"
disable-model-invocation: true
context: fork
---

# PRP Worklist

**Incubating.** Deliberately underspecified. Make your own judgements, then say what you chose
and why — the good choices get recorded and prescribed later. Do not wait for a spec that does
not exist yet.

Render the open issues and PRs of a repository as an artifact the maintainer can look at, and
offer it. Not a list of everything — a view of **what to take next**.

## The job

A tracker sorts by number and shouts every label equally loudly. That is the tool's view, not
the maintainer's. Produce the maintainer's view.

Read the tracker with `gh`. Then decide what is worth showing and how to show it.

## What this maintainer cares about

Considerations, not fields to emit. Weigh them, drop the ones that do not apply, add what the
repository makes obvious:

- **Blocked on a decision, or takeable now.** The distinction he asks for most.
- **Stale.** An issue whose premise has moved — the code it describes was deleted, the blocker
  it waits on closed. Staleness should be visible, not discovered on starting the work.
- **Near-duplicates.** Two issues that are one thing. Cheap to spot in a list, expensive to
  find after both are filed.
- **His, or someone else's.** Different obligations as a maintainer.
- **Blast radius** rather than severity. What breaks, and for whom, if this is left.

## Shape

Yours to decide. Markdown or HTML, grouped or ranked, dense or spacious — whatever makes the
answer to *"what do I take next"* obvious in a glance.

Then **offer it rather than pasting it**: write the file to this project's `~/.prp/<key>/` store
and print a link the operator can open. If a `helm-canvas` skill is available, follow it.

## Report your choices

End with a short note: what you grouped by, what you left out, what you could not tell from the
tracker alone. That note is the point of this skill being loose — it is how the shape gets
decided by evidence rather than up front.

If something here got in your way, say that too.
