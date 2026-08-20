# Agent Review Workflow

Review the target PR through specialist agents, then publish one evidence-based summary.

## 1. Resolve the PR and context

Resolve a number, URL, branch, or the current branch's PR with `gh pr view` / `gh pr list`. Read its
title, body, author, state, base, head, files, reviews, and comments.

- Stop when the PR is merged. Warn before reviewing a closed PR.
- Review a draft normally, but post a comment rather than approving or requesting changes.
- Check out the PR branch with `gh pr checkout` unless it is already checked out.
- For a full review, read the complete diff, repository guidance, full changed files, and directly
  relevant tests and precedents.
- Read matching implementation reports, completed plans, issue artifacts, and the previous canonical
  review under `$PRP_DIR` when they exist. Treat documented deviations as context, not automatic
  defects. On re-review, read every recorded finding disposition and its evidence.
- With `--verify-corrections`, use the previous report's `reviewed_head` and the current head to bound
  the correction diff. Read only the prior findings, their dispositions, that diff, and the direct
  context needed to verify them and detect correction-caused defects. If the previous head is missing,
  is not an ancestor, or the correction materially changes the outcome, architecture, or scope, run
  one full review instead and record why.
- If the only matching artifact is under a legacy `.claude/PRPs/` path, stop and tell the user to
  run the PRP home-store migration.

Do not edit files, resolve conflicts, rebase, commit, or push. Review the PR as it exists.

## 2. Run repository validation

Discover authoritative checks from repository guidance, package scripts, task runners, and CI.
For a full review, run the applicable type check, lint, tests, build, and any focused validation the
changed behavior requires. For correction verification, preserve still-applicable prior results and
rerun the focused check for every correction or disputed finding plus any authoritative gate the
correction could invalidate. Do not invent a generic command merely to fill a category.

Record the exact command, result, and decisive output. A missing or inapplicable check is `not run`,
not a pass. Distinguish a PR-caused failure from an unrelated or pre-existing failure when evidence
allows; otherwise report the uncertainty.

## 3. Select scopes

With no operator scope instruction, select `code`, `seams`, and `simplify`. Also select `types` when
the diff materially changes types, schemas, constructors or factories, public signatures, state
variants, or compiler escape hatches. Make that decision by reading the change rather than parsing
file extensions or keywords; skip it when no typed contract changed. Treat named or added scopes as
additive to the applicable defaults; “add tests” means those defaults plus `tests`. Treat an explicit
restriction as replacement; “only tests” means exactly `tests`. Honor any other explicit operator
inclusion or exclusion by intent rather than parsing fixed syntax.

In correction verification, retain any prior scope that owns a finding being verified unless the
operator explicitly narrows the pass; do not repeat other optional agents that had no affected finding.

| Scope | Agent | Focus |
|---|---|---|
| `code` | `prp-core:code-reviewer` | General correctness, sanity, scope, and repository fit |
| `seams` | `prp-core:seam-analyzer` | Missing types, counterpart drift, bypassed boundaries |
| `tests` | `prp-core:pr-test-analyzer` | Behavioral coverage and valuable regression protection |
| `comments` | `prp-core:comment-analyzer` | Accuracy and long-term value of changed comments |
| `errors` | `prp-core:silent-failure-hunter` | Swallowed failures, fallbacks, and actionable errors |
| `types` | `prp-core:type-design-analyzer` | Invalid states, semantic distinctions, boundary parsing, schema ownership, and exhaustive variants |
| `docs` | `prp-core:docs-impact-agent` | Stale or missing user and contributor documentation |
| `simplify` | `prp-core:code-simplifier` | Premature machinery and smaller coherent structures |

`all` selects every scope. Ignore `--agents`; it exists only so older callers still receive the
current default review.

## 4. Launch reviewers

Dispatch every selected agent in parallel when capacity permits, or sequentially when it does not. Every selected role remains required; wait for all of them before aggregation.
All agents are advisory and must not modify files or post their own PR comments.

Append this instruction to every reviewer prompt:

> Suggest `Critical`, `Important`, or `Suggestion` for each finding based on its actual consequence. The coordinator independently determines final severity and merge readiness.

In correction verification, give every selected agent the previous and current head SHAs, the bounded
diff, and the exact prior findings and dispositions relevant to its scope. Require it to verify those
findings and inspect the correction for regressions. Reopen a prior finding when evidence disproves
its disposition; allocate a new finding only for a defect caused by the correction. Do not review
unchanged parts of the original PR for unrelated findings.

When launching each agent via Task tool:

**prp-core:code-reviewer**:
> Review PR #<number> against its actual base and intended outcome. Return the general code review without modifying files or posting comments.

**prp-core:seam-analyzer**:
> Analyze PR #<number> for missing types at seams. Leave the diff to inspect direct counterparts of changed payloads, wire formats, persisted or resumed values, IPC/FFI and cross-language boundaries, syntax forms, validators, and synchronized enumerations. Enforce the two-sided evidence bar and documented carve-outs. Do not modify files, commit, or post comments.

**prp-core:pr-test-analyzer**:
> Map changed behavior in PR #<number> to existing unit, integration, and end-to-end assertions. Report only gaps with a plausible faulty implementation that current tests allow and the smallest behavioral test that would catch it. Do not modify files, commit, or post comments.

**prp-core:comment-analyzer**:
> Verify comments and docstrings changed by PR #<number> against actual code, contracts, and direct consumers. Report only materially false prose, a concrete maintenance trap, or missing durable knowledge that code and types cannot express. Do not modify files, commit, or post comments.

**prp-core:silent-failure-hunter**:
> Trace changed failure and recovery paths in PR #<number>. Report only reachable failures that become indistinguishable from success or lose evidence needed by the owner who can act; respect legitimate probes, retries, fallbacks, and propagation. Do not modify files, commit, or post comments.

**prp-core:type-design-analyzer**:
> Analyze changed typed contracts in PR #<number> for meaningful invariants or semantic distinctions they fail to enforce. Inspect reachable invalid construction, unsafe compiler escape hatches, boundary parsing, schema derivation, and exhaustive variant handling. Report only concrete downstream consequences and the smallest proportional enforcement point. Leave writer/reader drift and alternate boundary routes to the seam analyzer. Do not modify files, commit, or post comments.

**prp-core:docs-impact-agent**:
> Review repository documentation affected by PR #<number>. Report only materially false guidance or missing instructions required to discover, use, operate, migrate, or maintain changed public behavior. Determine this repository's real documentation surfaces and authoritative sources; do not treat steering files as changelogs. Do not modify files, commit, or post comments.

**prp-core:code-simplifier**:
> Review whether PR #<number> achieves its outcome through the smallest coherent structure. Check data shapes, ownership, concurrency, decision locality, threaded signals, call paths, and premature machinery. Report only evidence-backed smaller primitives that preserve the required behavior and meaningful invariants. Do not modify files, commit, or post comments.

## 5. Synthesize without re-reviewing

Read `../templates/review-report.md` before writing. Lead with the review's central signal: the
outcome, the few conclusions that determine readiness, and the common cause when findings converge.
Merge duplicate findings into one causal item, attribute every contributing agent, preserve meaningful
disagreement, and retain every distinct useful issue the agents found. Keep raw agent prose and
supporting paths in the finding's detail rather than the scanning layer. Record every selected scope,
including agents that returned no finding.

Write the synthesis in plain, concrete language. Cut generic praise, formulaic transitions, and vague
claims; use the repository's exact terms and name the behavior or consequence directly.

Treat agent labels as advisory evidence. Independently judge each finding by the actual consequence of
merging the current head:

- `Critical` — a plausible security compromise, data loss or corruption, widespread outage, or
  unrecoverable contract break on a supported path;
- `Important` — materially wrong, unsafe, or incomplete behavior on a reachable supported path, or a
  PR-caused failure of an authoritative merge gate; also a proved premature structural decision that
  creates material, durable state, ownership, or coordination cost disproportionate to the outcome;
- `Suggestion` — a useful observation that does not make the delivered outcome materially incorrect.

Weigh simplification while the change is still cheap to correct. A passing happy path does not make a
foundation sound: premature defensive machinery, tests for unsupported behavior, shared state,
duplicated representations, cross-layer signal threading, or a decision that needlessly closes future
options can harden into an expensive contract. Give that evidence real weight when a narrow, proven
smaller primitive removes the cost now. Do not elevate line-count reductions, stylistic alternatives,
speculative future reuse, or removal of tests that protect required behavior.

Repository guidance informs this judgment, but violating a written preference or process instruction
is not automatically blocking. The coordinator—not any individual reviewer—owns severity and the
readiness verdict.

Assign stable finding IDs (`R1`, `R2`, ...) on the first review. On re-review, preserve IDs for the
same causal finding, allocate new IDs after the prior maximum, verify each recorded disposition, and
never make an earlier finding disappear. Use only these states:

- `OPEN` — unresolved;
- `FIXED` — the changed head proves the correction;
- `NOT A FINDING` — decisive evidence disproves it or shows it was already satisfied;
- `TRACKED FOLLOW-UP` — valuable, separate work with a verified existing or newly created issue;
- `DECLINED` — non-actionable, speculative, overengineered, or directionally wrong, with a recorded reason.

Accept `TRACKED FOLLOW-UP` or `DECLINED` only when the independent evidence confirms the work is not
required by the PR's outcome or invariant. Otherwise keep the finding `OPEN`.

Do not invent findings, raise severity without evidence, or perform another code review during
aggregation. Synthesis connects and prioritizes reviewer evidence; it does not create new evidence.
In correction verification, reject a proposed new finding unless its evidence reaches the correction
diff and proves the correction caused it; a disproven disposition reopens its existing finding ID.
Carry the complete prior ledger forward even when only a subset of agents ran. State the verified
head range—or the reason for a full-review fallback—in the report's Signal.

Verdict rules:

- `READY TO MERGE`: no `OPEN` Critical or Important findings and all required validation passed.
- `NEEDS FIXES`: at least one `OPEN` Critical or Important finding, or a PR-caused required validation failure.
- `REVIEW INCOMPLETE`: required validation or decisive evidence could not be obtained.
- Suggestions never block by themselves.

Write the report to the expanded absolute path `$PRP_DIR/reviews/pr-{NUMBER}-review.md`.

## 6. Publish and report

Maintain one canonical GitHub issue comment for the complete report. When the previous canonical
report points to an existing issue comment on this PR—or a PR comment carries the template's
`prp-review-id` marker—edit that exact comment by ID; otherwise create it with `gh pr comment`. Do not
use “edit last” or append another complete report for a correction cycle. After first creation,
capture the stable URL, add it to the local report, update that same comment so its frontmatter
contains the URL too, and verify the local and GitHub bodies agree.

When `--approve` was explicitly requested and the verdict is `READY TO MERGE`, submit a concise formal
approval that links to the canonical comment. Submit a concise request-changes review linking to the
canonical comment only when explicitly requested or when the user explicitly asked for blocking
findings as a formal review. Never formally approve or request changes on a draft.

Read the PR back to verify the canonical comment exists and capture its stable URL. Replace
`publication: pending` in the local report and comment after first creation; on re-review, preserve the
existing URL. Then re-read the report and GitHub state to verify their bodies agree. Return the PR URL,
verdict, finding and disposition counts, validation summary, selected scopes, absolute report path,
and canonical comment URL.
