# Review Report Contract

Write the local report and canonical GitHub comment in this shape. Keep machine metadata inside the
HTML comment so downstream workflows can read it without making humans scan it.

```markdown
<!--
prp-review-id: pr-<number>
pr: <number>
base: <base branch>
head: <head branch>
reviewed: <ISO timestamp>
reviewed_head: <commit SHA>
verdict: <READY TO MERGE | NEEDS FIXES | REVIEW INCOMPLETE>
open_findings: <count>
scopes: [<selected scopes>]
publication: <verified canonical GitHub comment URL | pending>
-->

## <Ready to merge | Needs fixes | Review incomplete>

<One concise paragraph explaining the outcome, the conclusions that determine readiness, and any
common cause connecting the findings.>

**<count> blocking · <count> non-blocking**

**Validation:** <concise status>

<When applicable: **Resolved:** <count> · **Tracked follow-ups:** <issue links>>

### Findings

<Use the table when findings exist; otherwise write "No findings.">

| ID | Severity | Finding | State |
|---|---|---|---|
| `R1` | Critical / Important / Suggestion | <one-line impact> | OPEN / FIXED / NOT A FINDING / TRACKED FOLLOW-UP / DECLINED |

<Repeat this block for every distinct issue.>

<details>
<summary><code>R1</code> — <short finding></summary>

**Impact:** <observable consequence>

**Evidence:** `path:line`, <decisive validation or causal path>

**Required outcome:** <smallest valid correction, or why no correction is required>

**Found by:** `prp-core:<agent>`[, `prp-core:<agent>`]

**Disposition:** <state, reason, verifying evidence, and issue link when tracked>

</details>

<details>
<summary>Validation and reviewer coverage</summary>

#### Reviewer coverage

| Scope | Result |
|---|---|
| <selected scope> | <finding IDs or No additional findings> |

#### Validation

| Command | Result | Evidence |
|---|---|---|
| `<actual command>` | PASS / FAIL / NOT RUN | <decisive detail> |

</details>
```

Rules:

- Preserve every machine-metadata key and keep `verdict`, `open_findings`, and `publication` on exact
  unindented lines; deterministic consumers parse them from the raw report.
- Every Critical or Important finding needs a concrete impact and file:line evidence.
- Every distinct useful issue returned by an agent appears once. Merge duplicates and attribute all
  contributing agents; validation failures use `validation`.
- Preserve finding IDs across re-reviews. Never delete a prior finding; update its state and evidence.
- Keep `open_findings` equal to every `OPEN` row, including non-blocking Suggestions; autonomous
  callers use it to finish dispositioning a review that is otherwise ready.
- Keep suggestions genuinely optional. Never disguise a blocker as a suggestion or vice versa.
- A tracked follow-up requires a verified GitHub issue. A declined finding requires a concrete reason;
  do not create issues for speculative defense-in-depth, overengineering, or unclear direction.
- Keep a finding open when a proposed follow-up or decline would leave the PR's outcome or invariant
  unsatisfied.
- Record every selected scope and actual validation result inside the collapsed coverage section.
- Do not add generic praise, boilerplate checklists, confidence scores, or AI attribution.
- Write `publication: pending` before the first post. After GitHub verification, replace it in both the
  local report and canonical comment with the stable comment URL.
