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

<One sentence: the outcome and the conclusion that decides it.>

**<count> blocking · <count> non-blocking**

**Validation:** <concise status>

<When applicable: **Resolved:** <count> · **Tracked follow-ups:** <issue links>>

**Signal:** <The rest of the reasoning, in one short paragraph: the risk call behind the selected
scopes, the verified head range or why a full review ran instead, the common cause connecting the
findings, and what checked clean. Leave out what does not apply.>

### What changed

**User-visible:** <what a user or operator of the product now sees or does differently, or "None">

**Boundaries:** <the parts that appeared, disappeared, or now connect differently, or "None moved">

| Part | Kind | State | Connects to | Change |
|---|---|---|---|---|
| `<name as the repository spells it>` | module / type / wire / data | new / changed / removed / unchanged | <other Parts in this table it calls, reads, or writes> | <one line; blank when unchanged> |

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

**Required outcome:** <smallest valid correction covering every member below, or why no correction is required>

**Class:** <omit unless one invariant has several members. The invariant, the search that enumerated it, every affected member, every member examined and found clean.>

**Found by:** `<agent>`[, `<agent>`]

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
- What changed describes the PR; it judges nothing and adds no finding. A Part is one unit the diff
  touches at its edge: a module or directory (`module`), a type or schema shared across files
  (`type`), a wire format, protocol, or CLI surface (`wire`), or stored data or a file format
  (`data`). Group files into the unit they belong to, and keep the table to the parts a reader needs
  to see the shape, usually under eight rows. List an unchanged Part only when a changed one connects
  to it, and name connections only by Parts in the table.
- Every Critical or Important finding needs a concrete impact and file:line evidence.
- A finding that closes a causal class states the invariant, the search that enumerated it, every
  affected member, and every member examined and found clean, and its required outcome covers the
  class rather than the instance. A member nobody examined is unexamined, never clean.
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
