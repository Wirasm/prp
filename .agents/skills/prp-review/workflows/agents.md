# Agent Review Workflow

Review the target PR through specialist agents, then publish one evidence-based summary.

## 1. Resolve the PR and context

Resolve a number, URL, branch, or the current branch's PR with `gh pr view` / `gh pr list`. Read its
title, body, author, state, base, head, files, reviews, and comments.

Capture `headRefOid` as `reviewed_head`. Use that same immutable head for repository validation and
every reviewer.

Work only in a checkout this review created. Fetch the head, then add a detached worktree pinned to it:

```bash
git fetch origin <headRefName>
git worktree add --detach .worktrees/review-pr-<number> <reviewed_head>
git -C .worktrees/review-pr-<number> rev-parse HEAD   # must equal reviewed_head
```

Detach instead of checking out the branch. A delivery owner usually holds that branch, and git refuses
the same branch in two worktrees, so a branch checkout leaves only two moves: take over the owner's
tree, or detach. Detaching also makes `rev-parse HEAD` equal `reviewed_head` by construction, so no
reset is ever needed to reach the reviewed head.

Remove the checkout with `git worktree remove .worktrees/review-pr-<number>` as the review's last act,
including when the review stops early. The canonical report lives under `$PRP_DIR` and outlives it.

- Stop when the PR is merged. Warn before reviewing a closed PR.
- Review a draft normally, but post a comment rather than approving or requesting changes.
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

Never run a tree-moving command outside this review's own checkout. `gh pr checkout`, `git checkout`,
`git reset`, and `git stash` move whichever tree they run in; a delivery owner is often working in that
tree, and moving its HEAD silently reverts committed work. When the review's checkout is missing,
create it again rather than working wherever the shell happens to be.

## 2. Run repository validation

Run every check in the review's own checkout. Discover authoritative checks from repository guidance,
package scripts, task runners, and CI.
For a full review, run the applicable type check, lint, tests, build, and any focused validation the
changed behavior requires. For correction verification, preserve still-applicable prior results and
rerun the focused check for every correction or disputed finding plus any authoritative gate the
correction could invalidate. Do not invent a generic command merely to fill a category.

Record the exact command, result, and decisive output. A missing or inapplicable check is `not run`,
not a pass. Distinguish a PR-caused failure from an unrelated or pre-existing failure when evidence
allows; otherwise report the uncertainty.

## 3. Select scopes

With no operator scope instruction, select `code`, `seams`, and `simplify`. Those three are the
standing review. The seam reviewer owns type design, including a type that admits a state the code
forbids, so there is no separate types scope; an operator asking for `types` gets `seams`. Treat
named or added scopes as additive to the applicable defaults; “add tests” means those defaults plus `tests`. Treat an explicit
restriction as replacement; “only tests” means exactly `tests`. Honor any other explicit operator
inclusion or exclusion by intent rather than parsing fixed syntax.

In correction verification, retain any prior scope that owns a finding being verified unless the
operator explicitly narrows the pass; do not repeat other optional agents that had no affected finding.

| Scope | Agent | Focus |
|---|---|---|
| `code` | `code-reviewer` | General correctness, sanity, scope, and repository fit |
| `seams` | `seam-analyzer` | Missing types, counterpart drift, bypassed boundaries |
| `tests` | `pr-test-analyzer` | Behavioral coverage and valuable regression protection |
| `comments` | `comment-analyzer` | Accuracy and long-term value of changed comments |
| `errors` | `silent-failure-hunter` | Swallowed failures, fallbacks, and actionable errors |
| `docs` | `docs-impact-agent` | Stale or missing user and contributor documentation |
| `simplify` | `code-simplifier` | Premature machinery and smaller coherent structures |

`all` selects every scope. Ignore `--agents`; it exists only so older callers still receive the
current default review.

## 4. Launch reviewers

Dispatch every selected agent in parallel when capacity permits, or sequentially when it does not. Every selected role remains required; wait for all of them before aggregation.
All agents are advisory and must not modify files or post their own PR comments.

Spawn every selected agent in its named reviewer role. Do not paraphrase the role's defect class in the
launch prompt; the agent definition owns it. Give every reviewer this shared instruction:

> Review PR #<number> at exact head `<reviewed_head>` against its actual base. Work only in `<review checkout path>`; never run a command that moves any other tree. Do not follow a newer head. Suggest `Critical`, `Important`, or `Suggestion` for each finding based on its actual consequence. When one finding proves that a member of a finite class violates an invariant, enumerate that class with a deterministic repository search before reporting, and return one finding naming the invariant, the search you ran, every affected member, and every member you examined and found clean; a member you could not examine is unexamined, never clean. The coordinator independently determines final severity and merge readiness. Do not modify files, commit, or post comments.

Persist what each reviewer returns. This review's round is `1` when `$PRP_DIR/reviews/pr-<number>/`
holds no `round-*` directory, and one higher than the largest otherwise. Create
`$PRP_DIR/reviews/pr-<number>/round-<n>/` and write every reviewer's report to `<scope>.md` there,
verbatim, including a scope that reported no finding. The coordinator does the writing: reviewers stay
advisory and write nothing, to the store or the repository.

In correction verification, give every selected agent the previous and current head SHAs, the bounded
diff, and the exact prior findings and dispositions relevant to its scope. Require it to verify those
findings and inspect the correction for regressions. Reopen a prior finding when evidence disproves
its disposition; allocate a new finding only for a defect caused by the correction. A corrected
comment or documentation finding closes when the new text is accurate; improvable wording is neither
a disproven disposition nor a correction-caused defect. When a prior finding recorded a class, spend
one deliberate probe on the enumeration's completeness instead of hunting siblings fresh: a member it
missed reopens that finding rather than allocating a new one. Do not review unchanged parts of the
original PR for unrelated findings.

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

Close a proved causal class before publishing. When an aggregated Critical or Important finding
proves that one member of a finite class violates an invariant and no reviewer enumerated that class,
run the enumeration yourself as focused validation: a deterministic repository search, recorded in the
validation table with its command and decisive result. Carry the invariant, every affected member, and
every member examined and found clean into the finding, and let the required outcome cover the class
rather than the instance. This is how a class closes in one round instead of surfacing one sibling per
correction round. Physical proximity, shared file ownership, and "easy while here" are not a causal
class, and closing one is not permission to review unrelated code.

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

Write the report to the expanded absolute path `$PRP_DIR/reviews/pr-{NUMBER}-review.md`, then copy it
to `$PRP_DIR/reviews/pr-{NUMBER}/round-{n}/report.md`. The canonical path always holds the current
report; the round directory keeps what each round actually said.

## 6. Publish and report

Immediately before publication, re-read the live `headRefOid`. Publish only when it still equals
`reviewed_head`. If it changed, discard the candidate verdict and rerun a full review on the new head;
when that cannot finish, publish `REVIEW INCOMPLETE` rather than claiming current-head coverage.

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

Append this round to `$PRP_DIR/reviews/rounds.jsonl`, creating the file when absent, as one JSON
line and never rewriting an earlier one:

```json
{"pr":2879,"round":3,"reviewed_head":"<sha>","reviewed":"<ISO timestamp>","verdict":"NEEDS FIXES","scopes":["code","seams","simplify"],"findings":[{"id":"R1","severity":"Critical","state":"FIXED","found_by":["seams","code"],"class_members":4}]}
```

`found_by` names scopes, not agents, and carries every contributing scope. Omit `class_members` unless
the finding enumerated a class. A scope that ran and found nothing appears in `scopes` and in no
`found_by`; that absence is the measurement, so record the scopes that ran even when the round found
nothing at all.

Read the PR back to verify the canonical comment exists and capture its stable URL. Replace
`publication: pending` in the local report and comment after first creation; on re-review, preserve the
existing URL. Then re-read the report and GitHub state to verify their bodies agree. Return the PR URL,
verdict, finding and disposition counts, validation summary, selected scopes, absolute report path,
and canonical comment URL.
