# Evidence

A spike's authority comes entirely from its evidence. A confident verdict with weak evidence is worse than no spike — it gets believed.

## Standards

| Counts as evidence | Does not |
|---|---|
| Command output actually run, pasted | "This should work" |
| A measurement, with the conditions it was taken under | A number with no method |
| An error message hit, with what triggered it | "It would probably fail on..." |
| Observed behavior of the artifact | Behavior of the artifact as designed |
| A `file:line` in a real dependency's source | Recollection of how a library behaves |
| A documented guarantee, cited | An assumed guarantee |

Every claim in the report traces to something observed. Where reasoning fills a gap, mark it as reasoning — the reader needs to know which parts would survive scrutiny.

## "It ran" is not "it works"

A running artifact proves the hypothesis held **under the conditions tried**. The distance between those conditions and production is the real finding, and naming it is the report's honesty test.

Before claiming PROVEN, state plainly:

- **What was stubbed** — every fake is a hole. A spike that mocked the thing it was supposed to test has proven nothing; a spike that mocked the login screen is fine. Know which one this is.
- **Scale tried vs scale expected** — ten records is not a million. If the volume was not realistic, the volume question is untested, not passed.
- **Conditions not exercised** — concurrency, failure of a dependency, cold start, hostile input, slow network.
- **Duration** — anything about leaks, drift, or accumulation is untested by a run that lasted seconds.

## Fair comparison

When the spike compares approaches, the comparison is the experiment and it is easy to rig without meaning to.

- **Fix the metric first.** Before building, name what wins: latency at a percentile, lines of code touched to add a feature, number of concepts a new developer must learn. A metric chosen afterwards will be the one the favourite happens to win.
- **Vary one thing.** Same data, same hardware, same conditions. An approach also written second, by a more informed author, is not being compared fairly.
- **Give each approach its best shot.** The failure mode is building the favourite properly and the alternative naively. If one approach is unfamiliar, research it to the same standard before building — a straw man proves nothing.
- **Repeat measurements.** One run is noise. Discard warmup, run enough times to see the spread, and report the spread rather than the best number.
- **Report the losers' strengths.** The useful outcome is often "A overall, but B's handling of X is worth stealing." A comparison that only ranks throws away most of what it learned.

Where the metric is taste rather than measurement — how an interaction feels, how an API reads — the artifact's job is to let a human judge, not to decide. Put the variants side by side, make switching trivial, and hand it over. Record whose judgement was applied and on what.

## Proving a negative

DISPROVEN carries a higher burden than PROVEN, because "I could not make it work" and "it cannot work" look identical from the inside.

Before reporting DISPROVEN, establish:

- **The approach was credible** — the way a competent engineer would do it, not the first thing tried.
- **The obvious alternatives were considered** — and why they fail too, or why they were not tried.
- **The wall is structural** — a property of the technology, the architecture, or the constraint. If the wall is "this was harder than expected", the finding is a cost estimate, not a disproof.
- **The failure is reproducible** — the exact command or condition, so the next person can check rather than trust.

Most honest disproofs are actually CONDITIONAL: it cannot work *given something being held fixed*. Name that thing. It is more useful than the disproof.

## Traps

- **Measuring the wrong layer.** A benchmark dominated by JSON serialization says nothing about the database being evaluated. Confirm the measurement is sensitive to the thing under test — change that thing and check the number moves.
- **Caching.** A second run hitting a warm cache, a memoized result, or a CDN measures the cache. Especially deceptive across variants when one is warmed by the other.
- **The stub that hid the hard part.** Mocks migrate toward whatever was difficult. Re-read every stub against the hypothesis before concluding.
- **Synthetic data.** Uniform, clean, small generated data hides exactly the distribution problems, encoding edge cases, and skew that break the real thing.
- **Confirmation drift.** After investment in an approach, ambiguous results read as success. The pre-committed kill criteria exist for this moment — re-read them before deciding, not after.
- **The artifact becoming the point.** Time spent polishing something that will be thrown away is time not spent on evidence. Build ugly, learn fast.

## What is still unknown

Every spike ends with an explicit list of what it did not settle. This is not a disclaimer — it bounds the spike's authority and prevents a narrow result being read as a general one.

Include the conditions never exercised, the parts stubbed, the scale untested, and any question the spike raised without answering. A spike that surfaces a better question than it started with has done well; that only lands if the question is written down.
