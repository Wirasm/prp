# Review Report Contract

Write every review report in this shape. Omit empty finding rows, but keep all headings so humans and
downstream workflows can find the verdict, finding ledger, and validation reliably.

```markdown
---
pr: <number>
base: <base branch>
head: <head branch>
reviewed: <ISO timestamp>
reviewed_head: <commit SHA>
verdict: <READY TO MERGE | NEEDS FIXES | REVIEW INCOMPLETE>
open_findings: <count>
scopes: [code, seams, ...]
publication: <verified canonical GitHub comment URL | pending>
---

<!-- prp-review-id: pr-<number> -->

# PR Review: #<number> — <title>

## Signal

<One concise paragraph explaining the outcome, the central review conclusion, and any common cause
connecting the findings. Lead with what determines readiness.>

- **Blocking:** <count>
- **Non-blocking:** <count>
- **Resolved since previous review:** <count or Not applicable>
- **Tracked follow-ups:** <count and issue links, or None>
- **Validation:** <concise status>

## Findings

| ID | Severity | Finding | State |
|---|---|---|---|
| `R1` | Critical / Important / Suggestion | <one-line impact> | OPEN / FIXED / NOT A FINDING / TRACKED FOLLOW-UP / DECLINED |

## Detailed Findings

<Repeat this block for every distinct issue. Keep the scanning summary above concise.>

<details>
<summary><code>R1</code> — <short finding></summary>

**Impact:** <observable consequence>

**Evidence:** `path:line`, <decisive validation or causal path>

**Required outcome:** <smallest valid correction, or why no correction is required>

**Found by:** `<agent>`[, `<agent>`]

**Disposition:** <state, reason, verifying evidence, and issue link when tracked>

</details>

## Agent Coverage

| Scope | Result |
|---|---|
| code | <finding IDs or No additional findings> |
| seams | <finding IDs or No additional findings> |
| <requested scope> | <finding IDs or No additional findings> |

## Validation

| Command | Result | Evidence |
|---|---|---|
| `<actual command>` | PASS / FAIL / NOT RUN | <decisive detail> |

## Verdict

**<READY TO MERGE | NEEDS FIXES | REVIEW INCOMPLETE>**

<What must happen next, or why the PR is ready.>
```

Rules:

- Every Critical or Important finding needs a concrete impact and file:line evidence.
- Every distinct issue returned by an agent appears once in Findings and Detailed Findings. Merge
  duplicates and attribute all contributing agents; validation failures use `validation`.
- Preserve finding IDs across re-reviews. Never delete a prior finding; update its state and evidence.
- Keep `open_findings` equal to every `OPEN` row, including non-blocking Suggestions; autonomous
  callers use it to finish dispositioning a review that is otherwise ready.
- Keep the signal and finding ledger scannable. Put supporting paths and raw reviewer detail inside
  the collapsed finding block.
- Keep suggestions genuinely optional. Never disguise a blocker as a suggestion or vice versa.
- A tracked follow-up requires a verified GitHub issue. A declined finding requires a concrete reason;
  do not create issues for speculative defense-in-depth, overengineering, or unclear direction.
- Keep a finding open when a proposed follow-up or decline would leave the PR's outcome or invariant
  unsatisfied.
- Do not add generic praise, boilerplate checklists, confidence scores, or AI attribution.
- Write `publication: pending` before the first post. After GitHub verification, replace it in both the
  local report and canonical comment with the stable comment URL; downstream automation treats that
  URL as required delivery evidence.
