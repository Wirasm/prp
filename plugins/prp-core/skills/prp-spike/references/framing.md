# Framing the Spike

The framing decides whether the spike is worth running. Everything downstream is cheap to redo; this is not.

## The falsifiability test

A hypothesis qualifies when a specific observation would make it false, and that observation is plausible enough to be worth looking for.

Apply two checks:

1. **Name the disproof.** "What would I have to see to stop believing this?" No answer means it is a topic, not a hypothesis.
2. **Check both outcomes change something.** If PROVEN and DISPROVEN lead to the same next action, the question is not load-bearing. Do not spend a spike on it.

## Vague to falsifiable

| Vague request | Falsifiable hypothesis |
|---|---|
| "Can we use X?" | "X can do <specific job> against <our real constraint> without <the thing we fear>." |
| "Is this fast enough?" | "<Operation> completes within <budget> at <realistic volume> on <representative hardware>." |
| "Would this feel better?" | "Users can complete <task> in this interaction model without hitting <the confusion we predict>." |
| "Should we adopt Y?" | "Y handles <the two cases our current thing handles badly> without losing <the case it handles well>." |
| "Can our schema support Z?" | "Z is representable in the current schema without a migration and without a denormalized write path." |

The pattern: replace the adjective with a threshold, and name the failure being feared. "Fast enough", "clean", "better", "scalable" are all placeholders for a number or a named condition that has not been decided yet. Deciding it is part of the framing, not the build.

## Kill criteria

Write, before building, the observations that would end the spike as DISPROVEN. Good kill criteria are:

- **Observable** — a measurement, an error, a behavior seen, not a feeling.
- **Pre-committed** — fixed before results exist. A threshold chosen after seeing the number is not a threshold.
- **Plausible** — at least one must be a real possibility. If every kill criterion is far-fetched, the hypothesis is trivially true and the spike is theatre.

Where a threshold is genuinely unknown, say so explicitly and record the number the spike produces as a **finding** rather than a pass/fail. A spike that establishes the baseline is legitimate; one that invents a threshold to clear afterwards is not.

## Question archetypes

The question type shapes what evidence will be needed. It does not dictate what to build — that follows from what would falsify the claim.

**Feasibility** — can this be done here at all? Evidence is a working (ugly) path through the hardest part. Aim the build at the step most likely to be impossible, not the first step.

**Fit** — does this belong in our stack? Feasibility is usually not in doubt; the question is what it costs in friction. Evidence is the integration seam actually built: where it fights the existing abstractions, what it forces elsewhere, what it would make harder forever.

**Constraint / primitive** — see below.

**Comparison** — which approach wins? The metric that decides it is fixed and recorded during framing, before any variant exists; a metric chosen afterwards will be the one the favourite happens to win. The build then has to give every approach its best shot, or it proves nothing.

## Constraint questions

"Is it worth changing X to allow Y" is a different question from "is Y possible", and it is the one most often mis-framed as the other. Treat the constraint as the variable.

Frame it as: **"Y is impossible under <constraint C>, and possible under <specific relaxation of C>."** Then the spike has two jobs — demonstrate the wall, and demonstrate that moving it actually helps. Skipping the first produces a proposal to change a primitive with no evidence the primitive was the obstacle.

The report has to price the change, not just prove it works:

- **What exactly changes** — the primitive, schema, dependency, or product rule, stated precisely enough to estimate.
- **Blast radius** — what else depends on the current behavior, and what breaks or needs migrating.
- **What else it unlocks** — a constraint blocking one feature usually blocks others. This is often what tips the decision, and a spike scoped to one feature is the thing most likely to miss it.
- **The reversible option** — whether the same result can be had behind a flag, an adapter, or a narrower change. Usually worth one attempt before recommending surgery on a primitive.

A constraint spike that reports "we should change C" without blast radius has done half the work. The decision is a trade, so the evidence must cover both sides.

## Splitting — on the falsifier, not the claim count

**The unit of a spike is one falsifier, not one sentence.** A question with several sub-claims that a *single* artifact can test is one spike. Sub-claims each needing their own setup are separate spikes.

Getting this backwards is expensive in both directions. Split what shares a falsifier and every agent redoes the same setup — N times the cost, not a fraction of it. Merge what does not and one artifact grows until it tests nothing sharply.

**One falsifier, several claims → one spike.** Build it once and report **a verdict per sub-claim**; the mix is the output, and it is normal for a mechanism probe to come back part PROVEN, part DISPROVEN, part CONDITIONAL. List the sub-claims in the frame so each has something to be judged against, and record the seat each was proved from (`evidence.md`) — sub-claims usually differ in *where* they were observed, not in what was built.

**Separate setups → separate spikes.** Split into 2–5, each independently falsifiable, and **run the riskiest first** — disproving it makes the rest unnecessary. Order by *probability of failure*, not by build order or by what is easiest. The cheapest spike is the one never run because an earlier one closed the path. One run answers one falsifier: take the riskiest here and list the rest in the report's Recommendation as follow-up spikes.

Signals a spike is genuinely several:
- The sub-claims need **different artifacts**, environments or fixtures to test.
- One sub-claim cannot be reached until another has been answered — that is a sequence, not a set.
- One part is nearly certain and another is a coin flip — the certain part is padding.

A long hypothesis is **not** a signal by itself. "A and B and C" about one mechanism, testable by one artifact, is one spike with three sub-claims.

## Sizing

The spike ends when the question is answered — not at a time box, and not when the artifact feels finished.

- **Answered early is done.** If the first thing built disproves the hypothesis in twenty minutes, that is the ideal outcome. Do not keep building to justify the exercise.
- **No end in sight means re-frame.** A spike that keeps growing is usually answering an unfalsifiable question, or several at once. Return here and split.
- **Blocked on access, not knowledge, is not a spike.** Missing credentials, a licence, or a decision only a human can make is a blocker to report, not a thing to work around with a mock — a mock of the unknown part proves nothing about it.
