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

1. A spike answers **one falsifiable question** — or several sub-claims that share a single falsifier. No falsifiable question, no spike.
2. Kill criteria are written **before** the build. Deciding what counts as failure after seeing results turns a spike into a rationalization.
3. **DISPROVEN is a success.** It bought a decision with evidence and closed a path that would otherwise have cost weeks.
4. Spike code is throwaway by construction and **never opens a PR**.

## Phase 1 — Frame

Convert the request into a claim that can fail, and fix the kill criteria before touching code.

**Reconnaissance before framing is allowed, and usually required.** A hypothesis that names a version, a field, a threshold, or a mechanism cannot be written cold — read the issue, the source, and the environment until the claim can be stated precisely. The line is the **falsifier**: never let findings produced by the thing built to test the claim reshape the claim. Recon sharpens the question; results must only answer it.

Produce four things:

- **Hypothesis** — one sentence, falsifiable, specific enough that two people would agree on whether it held.
- **Slug** — 2–4 lowercase hyphenated words from the hypothesis. It names the branch, the worktree, and the report file; derive it once here and reuse it everywhere.
- **Kill criteria** — the specific observations that would end this as DISPROVEN, fixed now rather than after results exist.
- **Boundaries between verdicts** — what separates PROVEN from CONDITIONAL, and CONDITIONAL from DISPROVEN. The kill criteria say what failure looks like; this says which *kind* of failure it is. Deciding that boundary after seeing results is how CONDITIONAL gets rounded to whichever verdict is more convenient.

**Split on the falsifier, not the claim count.** Sub-claims one artifact can test together are **one** spike — build it once, list them in the frame, and report a verdict per sub-claim, because the mix is the output. Sub-claims each needing their own setup are separate spikes: take the **riskiest first** here, and list the rest in the report's Recommendation as follow-up spikes. For the framing craft (vague-to-falsifiable rewrites, constraint questions, splitting, sizing), read `references/framing.md`.

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

**If already in an isolated worktree** — spawned there by an orchestrator — stay put and do not nest a second one. `EnterWorktree` is unavailable to a pinned agent; where a branch name is wanted, plain `git switch -c spike/<slug>` inside the current worktree is enough.

Otherwise use the prp-worktree skill to create a worktree named `spike/<slug>` and work there. A spike branch is never merged.

`--here` skips isolation entirely — use it only when a fresh checkout cannot run the project (gitignored build prerequisites, an expensive bootstrap, a running local stack). Record in the report that it was used and why, and leave the checkout as it was found.

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

Reach one top-level verdict for the original hypothesis. When sub-claims have mixed results, keep each sub-claim's own verdict and use the top-level verdict to answer whether the original hypothesis held:

| Verdict | Meaning |
|---|---|
| **PROVEN** | Holds within current constraints. Evidence attached. |
| **DISPROVEN** | Does not hold. Name the wall it hit and why it is not the approach's fault. |
| **CONDITIONAL** | Holds only if a named constraint changes. Name the constraint, the cost of changing it, and what else that change would unlock. |

**CONDITIONAL is the verdict most spikes should reach and most reports dodge.** "Impossible" is usually shorthand for "impossible without changing something we were treating as fixed" — a primitive, a schema, a dependency, a product rule. Surfacing that trade is the point: it converts a dead end into a priced decision. Never collapse it into DISPROVEN. Never let it drift into PROVEN by quietly assuming the change is free.

**Label each verdict `proved` or `inferred`, and record the seat it was proved from** — which process, layer or surface, under which mode. Then re-run the inferred ones before finalizing: the setup already exists by this point, and an inference is where a spike is most confidently wrong. `references/evidence.md` carries the craft, including what to do when a kill criterion turns out to have named the wrong observation points.

Complete `$PRP_DIR/spikes/spike-<slug>.md` — read `templates/spike-report.md` again (mandatory) and fill every remaining section, replacing `(pending)` with the verdict. Keep every heading except `## Conditional constraint`, which exists only for a CONDITIONAL top-level verdict.

**One report, at that path.** The Phase 1 file *is* the report — finish it in place. Do not write a second copy under `research/`, `reports/`, or anywhere else: a stub pointing at a fuller document elsewhere splits the record, and nothing keeps the two in agreement.

## Phase 7 — Dispose

**The evidence's permanent home is the store.** Copy whatever the verdict rests on — harness scripts, fixtures, captured output — into `$PRP_DIR/spikes/<slug>/`. It survives a discarded worktree, is shared across the project's worktrees, and needs no git operation an isolated agent may be unable to perform.

But `$PRP_DIR` is **local-only**, so a store path is unfollowable by anyone else. Read `references/handoff.md` for the routes that make evidence followable off this machine — a secret gist when the verdict travels somewhere others read, a branch only when the spike code is substantial enough to re-run — and for the `--here` patch capture.

- **Never open a PR.** Every other terminal skill in this pack ends in one; this one ends in a verdict.
- Do not fold spike code into production. A validated approach gets **rewritten** under normal standards, by `prp-plan` and `prp-implement`.
- **Verify the Evidence pointer before calling the report done.** A named branch must exist and carry a commit; otherwise point at the store directory. Evidence that cannot be followed is a claim, not a result.
- Leave the worktree in place if the user may want to poke at it; otherwise tear it down with the prp-worktree skill.

## Phase 8 — Route the verdict

A spike that ends in the operator's terminal changes nothing. Propose where the verdict should land — a comment on the issue that commissioned it, a new item when the spike started from free text and nothing fits, or nothing at all when the question is closed and no work follows.

**Propose; do not act.** Creating or commenting on a tracker item is outward-facing, and this skill's terminal act is a verdict — never a merge, a PR, or an unrequested ticket. `references/handoff.md` has the routing table and what each verdict should ask for; a CONDITIONAL in particular must be framed as a decision, not filed as a task.

Report to the user: the hypothesis, the verdict, the two or three pieces of evidence that decided it, where the evidence lives, the report path, and the proposed destination. Lead with the verdict.

## Gotchas

- **The build phase eats spikes.** Producing something impressive rather than something decisive is the default failure. Return to the hypothesis whenever the next step is unclear.
- **A working artifact is not a PROVEN hypothesis.** It proves only what it exercised.
- **Spike effort does not estimate real effort.** Something built in an hour without tests, error handling, or edge cases is not an hour of work. Say this wherever the report could be read as a plan.
- **Do not let a spike become the implementation.** When the verdict is PROVEN and the code looks decent, the pull to keep going is strong. Stop and hand off.

## Resources

- `references/framing.md` — turning a vague idea into a falsifiable hypothesis with kill criteria; constraint and comparison questions; splitting and sizing
- `references/evidence.md` — evidence standards, fair comparisons, proving a negative, the traps that make spikes lie (mandatory read in Phase 1 for a comparison spike, before either variant is built; otherwise read in Phase 5)
- `references/handoff.md` — making evidence followable off this machine (store / gist / branch), and routing the verdict to where it changes something. Read in Phase 7–8
- `templates/spike-report.md` — the report to fill (mandatory read in Phase 1 to record the frame, and again in Phase 6 to complete it)
