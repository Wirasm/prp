# Spike Report Template

Written in two passes. In **Phase 1**, create the file with the header (verdict `(pending)`) and `## The question` filled in — that section is the pre-commitment and is never edited afterwards. In **Phase 6**, replace `(pending)` with the verdict and fill everything else.

Lead with the verdict — the reader wants the decision first and the working second.

Drop the CONDITIONAL section when the verdict is not CONDITIONAL. Keep every other section: the ones that bound the result are the ones a reader most needs and an author most wants to skip.

---

```markdown
# Spike: {question in a few words}

**Verdict**: {(pending) until Phase 6 — then PROVEN | DISPROVEN | CONDITIONAL}
**Hypothesis**: {the falsifiable claim, as committed before the build}
**Date**: {YYYY-MM-DD}
**Under test**: {exact versions of everything the result depends on — runtime, dependency, protocol, OS, arch. This is what makes the verdict re-checkable when one of them moves. Omit only if nothing external can change under it.}
**Evidence**: `{spike/<slug>}` {or, under --here: `spikes/spike-<slug>.patch` — no branch}

## Verdict

{2–4 sentences. What was established, and the single piece of evidence that decided it. If CONDITIONAL, name the constraint here — do not make the reader hunt for it.}

## The question

{Why this was worth a spike: the decision waiting on it, and what each outcome would change.}

**Kill criteria** (committed before building):
- {observation that would have disproven it}
- {…}

**Verdict boundaries** (committed before building):
- PROVEN if {…} · CONDITIONAL if {…} · DISPROVEN if {…}

{In Phase 6: which kill criteria fired, or that none did. If one turned out to name the wrong
observation points, say so here as its own finding — do not rewrite the criterion.}

## Where each verdict was proved from

{One row per verdict. `Seat` = the process, layer or surface it was observed at, and under which
mode. `Basis` = proved (this spike observed it) or inferred (reasoned from elsewhere). Re-run the
inferred ones before finalizing; anything left inferred stays labelled and says why it could not be
converted.}

| Claim | Verdict | Seat | Basis |
|---|---|---|---|
| {A1 …} | {PROVEN} | {at the hook, default mode} | proved |
| {A2 …} | {CONDITIONAL} | {sender side, --flag set} | inferred — {why not converted} |

## What was built

{The artifact, in a few lines: what it does, aimed at which risk. Where it lives on the branch, and the command to run it.}

**Approach**: {the approach taken and why it is a credible one — what a competent engineer would do here.}

## Evidence

{Observed results only. Commands run with their output, measurements with the conditions they were taken under, errors hit with what triggered them. Where reasoning fills a gap, mark it as reasoning.}

{For a comparison: the metric fixed before building, the conditions held equal, results including spread, and what the losing approaches did better.}

## The constraint

**What must change**: {the primitive, schema, dependency, or product rule — precisely enough to estimate}

**Evidence it is the obstacle**: {the wall demonstrated, and that moving it helps}

**Blast radius**: {what depends on current behavior; what breaks or needs migrating}

**Also unlocks**: {other things this constraint currently blocks — often what tips the decision}

**Cheaper option tried**: {flag, adapter, or narrower change — and why it does or does not suffice}

## Limits of this result

- **By seat**: {what is untested *from a given vantage point* — a claim proved at the hook says
  nothing about the sender's side. Keep these separate from the overall limits below; collapsing
  them hides the narrower hole.}
- **Stubbed**: {every fake, and whether any of them covered part of the question}
- **Scale tried**: {vs the scale expected in production}
- **Not exercised**: {concurrency, dependency failure, cold start, hostile input, duration}

## Still unknown

- {question this spike did not settle}
- {question this spike raised}

## Recommendation

{What to do next, and what NOT to do. If PROVEN: the plan-and-implement path, and the parts of the real build this spike did not touch. If DISPROVEN: the path now closed, and what to try instead. If CONDITIONAL: the trade, stated as a decision someone can make.}

**Effort**: this spike took {duration} without tests, error handling, or edge cases. That is not an estimate for the real build. {What the real one additionally needs.}

## Reproducing

{Branch — or patch path and the commit it applies to, under --here. How to run it, what to look at. This is the evidence: anyone doubting the verdict should be able to check it rather than trust it.}
```
