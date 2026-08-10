---
name: prp-spike
description: Prove or disprove an idea by building the smallest throwaway artifact that could falsify it, in an isolated worktree, ending in a PROVEN / DISPROVEN / CONDITIONAL verdict backed by evidence - never a PR. Use when the user wants to "spike this", "build a proof of concept", "POC this", "prototype it to find out", asks "is this possible", "is this feasible", "does this fit our stack", or "would it be worth changing X to allow Y" and wants it settled by building rather than by analysis, wants to compare approaches on evidence before picking one, or invokes $prp-spike.
---

> **Arguments:** `$ARGUMENTS` (and `$1`, `$2`, ...) refer to the arguments given when this skill was invoked. Take them from the user's request; if absent, infer them from the conversation.

# PRP Spike — Prove or Disprove

Settle an open question by building the smallest thing that could prove it **wrong**. The deliverable is a verdict backed by evidence, not shippable code.

**Input**: $ARGUMENTS (if absent, take the question from the conversation).

## When to use

- **Feasibility** — can this be built at all, here, with what we have?
- **Fit** — does this sit naturally in our stack, or fight it the whole way?
- **Cost of admission** — what would have to change (a primitive, an abstraction, a product constraint) to make it possible, and is that trade worth it?
- **Choice** — which of several approaches survives contact with the real constraints?

Not for work whose feasibility is already settled — that is `prp-plan` then `prp-implement`. Not for something already broken — that is `prp-debug`.

## The contract

1. A spike answers **one falsifiable question**. No falsifiable question, no spike.
2. Kill criteria are written **before** the build. Deciding what counts as failure after seeing results turns a spike into a rationalization.
3. **DISPROVEN is a success.** It bought a decision with evidence and closed a path that would otherwise have cost weeks.
4. Spike code is throwaway by construction and **never opens a PR**.

## Phase 1 — Frame

Convert the request into a claim that can fail, and fix the kill criteria before touching code.

Produce four things:

- **Hypothesis** — one sentence, falsifiable, specific enough that two people would agree on whether it held.
- **Slug** — 2–4 lowercase hyphenated words from the hypothesis. It names the branch, the worktree, and the report file; derive it once here and reuse it everywhere.
- **Kill criteria** — the specific observations that would end this as DISPROVEN, fixed now rather than after results exist.
- **Boundaries between verdicts** — what separates PROVEN from CONDITIONAL, and CONDITIONAL from DISPROVEN. The kill criteria say what failure looks like; this says which *kind* of failure it is. Deciding that boundary after seeing results is how CONDITIONAL gets rounded to whichever verdict is more convenient.

If the idea carries several independent risks, split it and spike the **riskiest first** — a cheap disproof there saves the rest. One spike run answers one question: take the riskiest here, and list the rest in the report's Recommendation as follow-up spikes. For the framing craft (vague-to-falsifiable rewrites, constraint questions, splitting, sizing), read `references/framing.md`.

If the spike compares approaches, read `references/evidence.md` → **Fair comparison now**. The winning metric must be fixed and recorded here, before either variant exists — a metric chosen afterwards will be the one the favourite happens to win.

State the frame back to the user. When running interactively, confirm an ambiguous hypothesis before building — a spike that answers the wrong question is total waste, and framing is the cheapest thing to correct. When running unattended, record the interpretation chosen and the alternatives rejected, and proceed.

### Record the frame before building

Pre-commitment only counts if it outlives the conversation. Write the frame to disk now — a transcript does not survive compaction, and an agent that has seen its results can reconstruct criteria that flatter them.

```bash
# --- PRP store resolver (canonical; keep byte-identical across skills) ---
_gd="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"
case "$_gd" in */.git) _root="${_gd%/.git}" ;; "") _root="$PWD" ;; *) _root="$_gd" ;; esac
_root="$(cd "$_root" && pwd -P)"
_name="$(basename "$_root" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-*//;s/-*$//')"
PRP_DIR="${PRP_HOME:-$HOME/.prp}/${_name:-project}-$(printf %s "$_root" | git hash-object --stdin | cut -c1-8)"
mkdir -p "$PRP_DIR"; [ -f "$PRP_DIR/project.json" ] || printf '{"path": "%s", "name": "%s"}\n' "$_root" "${_name:-project}" > "$PRP_DIR/project.json"
mkdir -p "$PRP_DIR/spikes"
```

The resolver keys off the main repo, so the file lands in the shared store and stays readable from the main checkout while the spike branch is untouched.

Read `templates/spike-report.md` now (mandatory) and create `$PRP_DIR/spikes/spike-<slug>.md` with its header, `## The question` section, and `**Verdict**: (pending)`. Phase 6 fills in the rest; the hypothesis, kill criteria, and verdict boundaries recorded here are **never edited after this point**. The pending marker keeps an abandoned spike visibly unfinished instead of reading as a report with a missing verdict.

**GATE**: the file exists and contains the hypothesis, kill criteria, and verdict boundaries. Do not build without it.

## Phase 2 — Isolate

Spike code is disposable and often invasive. Keep it away from the working checkout.

Use the prp-worktree skill to create a worktree named `spike/<slug>`, and work there. The branch is the spike's home; it is never merged.

`--here` skips the worktree — use it only when a fresh checkout cannot run the project (gitignored build prerequisites, an expensive bootstrap, a running local stack). It changes how the spike is captured and torn down; see Phase 7. Record in the report that it was used and why.

## Phase 3 — Research

Read only enough to choose a **credible** approach — one a competent engineer would defend. A spike that fails because of a naive approach has proven nothing about the idea.

- Prefer primary sources: official docs, the dependency's actual source, specs, the codebase itself.
- Use `web-researcher` for anything outside the training cutoff, and `codebase-analyst` to learn how the relevant subsystem really works before assuming what it allows.
- Stop when the approach is defensible. Research is not the deliverable here; the build is.

## Phase 4 — Build the falsifier

Build the **smallest artifact that could prove the hypothesis wrong**, then stop.

The shape follows the question, not a catalogue — an interactive demo, a comparison of N implementations against a stated metric, a probe against a real API, a load harness, a type-level sketch, a patched dependency proving a primitive change works. Ask: *what would I have to see to stop believing this?* Build that.

Hold to:

- **Aim at the risk.** Build the part that might fail. Scaffolding, auth, styling, and persistence are not the question — stub them.
- **No production habits.** No tests, no error handling beyond what keeps it running, no abstractions. Every hour spent making spike code good is an hour not spent learning.
- **Real inputs.** Real data shapes, real API, real volumes. A spike on synthetic happy-path data proves nothing about production.
- **Surface the state.** Print or render what the artifact is doing, so the evidence is observable rather than asserted.
- **Track what got faked.** Every stub is a hole in the proof; the report has to name them.

## Phase 5 — Stress

A spike that only ran the happy path has not been tested — it has been demoed. Attack the claim where it is weakest.

Work the kill criteria from Phase 1 deliberately: push the volume, break the assumption the approach rests on, feed the edge case, pull the dependency. Most spikes earn their keep here.

For evidence standards — what counts as proof, how to make a comparison fair, and the traps that make spikes lie — read `references/evidence.md`.

## Phase 6 — Verdict

**Re-read the kill criteria and verdict boundaries recorded in Phase 1 before choosing — not after.** They were written by someone who had not yet seen these results. That is the only reason they are worth anything.

Reach one verdict:

| Verdict | Meaning |
|---|---|
| **PROVEN** | Holds within current constraints. Evidence attached. |
| **DISPROVEN** | Does not hold. Name the wall it hit and why it is not the approach's fault. |
| **CONDITIONAL** | Holds only if a named constraint changes. Name the constraint, the cost of changing it, and what else that change would unlock. |

**CONDITIONAL is the verdict most spikes should reach and most reports dodge.** "Impossible" is usually shorthand for "impossible without changing something we were treating as fixed" — a primitive, a schema, a dependency, a product rule. Surfacing that trade is the point: it converts a dead end into a priced decision. Never collapse it into DISPROVEN. Never let it drift into PROVEN by quietly assuming the change is free.

Complete `$PRP_DIR/spikes/spike-<slug>.md` — read `templates/spike-report.md` again (mandatory) and fill every remaining section, replacing `(pending)` with the verdict. Keep every heading; drop only the CONDITIONAL section when the verdict is not CONDITIONAL.

## Phase 7 — Dispose

Commit the spike to its branch, and push it if the repo has a remote. The branch **is** the artifact — the evidence behind the verdict, re-runnable by whoever doubts the result.

- **Never open a PR.** Every other terminal skill in this pack ends in one; this one ends in a verdict.
- Do not fold spike code into production. A validated approach gets **rewritten** under normal standards, by `prp-plan` and `prp-implement`.
- Leave the worktree in place if the user may want to poke at it; otherwise tear it down with the prp-worktree skill. The branch survives either way.
- **Under `--here` there is no spike branch.** Never commit to the branch that was already checked out. Capture the work as a patch — `git diff > "$PRP_DIR/spikes/spike-<slug>.patch"` (add `git diff --cached` and untracked files if either exists) — then restore the checkout to the state it was found in, and record the patch path where the report asks for a branch.

Report to the user: the hypothesis, the verdict, the two or three pieces of evidence that decided it, the branch or patch path, and the report path. Lead with the verdict.

## Gotchas

- **The build phase eats spikes.** Producing something impressive rather than something decisive is the default failure. Return to the hypothesis whenever the next step is unclear.
- **A working artifact is not a PROVEN hypothesis.** It proves only what it exercised.
- **Spike effort does not estimate real effort.** Something built in an hour without tests, error handling, or edge cases is not an hour of work. Say this wherever the report could be read as a plan.
- **Do not let a spike become the implementation.** When the verdict is PROVEN and the code looks decent, the pull to keep going is strong. Stop and hand off.

## Resources

- `references/framing.md` — turning a vague idea into a falsifiable hypothesis with kill criteria; constraint and comparison questions; splitting and sizing
- `references/evidence.md` — evidence standards, fair comparisons, proving a negative, the traps that make spikes lie (mandatory read in Phase 1 for a comparison spike, before either variant is built; otherwise read in Phase 5)
- `templates/spike-report.md` — the report to fill (mandatory read in Phase 1 to record the frame, and again in Phase 6 to complete it)
