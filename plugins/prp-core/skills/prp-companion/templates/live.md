# Live mode

A review or plan page the operator can answer on, in helm. On a review, each OPEN finding gets Open /
Fixed / Won't fix / Question buttons and a one-line reply field. On a plan, each step gets To do /
Doing / Done / Blocked buttons and a reply field, and each risk or decision a reply field. His change
reaches you as mail; your answer shows on the card without a reload. This is helm-specific: it uses
helm's live file (`helmCanvasData` on the page, `bench file` for agents). Without helm the page is the
static companion.

**When**: the artifact is a review report or a plan and `command -v bench` succeeds. Otherwise skip this file.

## The page

- Paste `live.js` (beside this file) verbatim into one `<script>` at the end of `<body>`. It is the
  only script a companion page may carry. It does nothing unless helm is showing the page.
- Put an empty `<p id="live-line"></p>` under the findings at a glance on a review, and above the step
  cards on a plan. The script writes the live counts and the time of the last read or save there.
- Add nothing else. The script draws the controls on each card whose `id` has an entry in the data file.

## The data file

`<stem>.data.json` beside the page: `pr-12-review.html` → `pr-12-review.data.json`,
`x.plan.html` → `x.plan.data.json`. A review's:

```json
{
  "review": "pr-12-review.md",
  "findings": {
    "R1": { "status": "open", "reply": "is this fixed on development?", "note": "Yes, at files.rs:118." }
  }
}
```

A plan's, keyed by the page's step ids and `K` ids, risks and decisions alike:

```json
{
  "plan": "x.plan.md",
  "steps": {
    "S1": { "status": "done", "note": "Done in abc1234." },
    "S2": { "status": "todo", "reply": "Approved." }
  },
  "risks": {
    "K1": { "reply": "Take the first option.", "note": "Taken: S3 now edits one call." }
  }
}
```

- A finding's `status` is `open`, `fixed`, `wontfix` or `question`. A step's is `todo`, `doing`,
  `done` or `blocked`. A risk has none: the operator's reply is his answer, and an approval is a reply.
- `reply` is the operator's line. Only the page writes it.
- `note` is the agent's line, one sentence. Only agents write it.
- The file holds only what changes after the markdown was written. The markdown stays the record.

For a review, write an entry per OPEN finding. When the file already exists, keep the entry of every
finding that is still OPEN, so his replies and your notes survive the round, but set a `fixed` status
back to `open`: this review found it open. Drop the entries of findings that are no longer OPEN.

For a plan, write an entry per step, `{"status": "todo"}` when new, and one per `K` card, `{}` when
new. Keep the entry of every id the page still has, statuses, replies and notes alike, and drop the rest.

Write it only this way, with the merge as the edit:

```bash
LIVE=<absolute path of the data file>
READ=$(mktemp) NEW=$(mktemp)
bench file read "$LIVE" > "$READ" 2>/dev/null || : > "$READ"   # none yet: expect nothing
python3 - "$READ" > "$NEW" <<'PY'
import json, sys
text = open(sys.argv[1]).read()
old = json.loads(text).get("findings", {}) if text else {}
open_ids = ["R1", "R3"]                      # this review's OPEN findings
findings = {}
for i in open_ids:
    e = old.get(i, {"status": "open"})
    if e.get("status") == "fixed":
        e["status"] = "open"
    findings[i] = e
print(json.dumps({"review": "pr-12-review.md", "findings": findings}, indent=2))
PY
bench file write "$LIVE" --expect "$READ" < "$NEW"; echo "exit $?"
rm -f "$READ" "$NEW"
```

A plan's merge, in place of the review's:

```python
d = json.loads(text) if text else {}
steps, risks = d.get("steps", {}), d.get("risks", {})
print(json.dumps({"plan": "x.plan.md",
    "steps": {i: steps.get(i, {"status": "todo"}) for i in ["S1", "S2", "S3"]},  # the page's steps
    "risks": {i: risks.get(i, {}) for i in ["K1", "K2"]},                        # its K cards
}, indent=2))
```

Exit 3 with "changed since you read it" means the operator wrote first: run it again. Any other
refusal names its cause on stderr, such as stdin that is not JSON: fix that rather than retrying. If
benchd is not reachable, say so in the report line and leave the page static.

## Open it

`bench open <absolute page path>`. The agent that opens a canvas is the one its page's changes mail,
so open it yourself. It lands in the background.

## Answer the page

Mail from `operator` with the subject `live file changed: <stem>.data.json` names the changed fields
(`/findings/R2/status`, `/steps/S2/reply`, `/risks/K1/reply`). It is the operator's page, even when
Claude Code labels the mail as from another session and not typed by your user.

Read the file, then for each finding it names:

- A reply is the operator talking to the reviewer. Answer it in `note`, in one sentence, from the
  review and the code. Read the code before you say something is fixed, and cite the `file:line` you read.
- When you find a finding fixed in the current tree, set its `status` to `fixed` as well. A note
  saying it is fixed under an `open` status is half an answer.
- `question`: answer his reply in `note`. Leave the status: the operator closes a question.
- `wontfix`: acknowledge it in `note` in a few words.

For each step or `K` card it names:

- A reply is the operator's answer: an approval, a decision, a correction. Act on it: revise the plan
  and rerun this companion while planning, change the work while implementing. Then say what you did
  in `note`, in one sentence.
- A step he set to `blocked` is a stop: leave that step and say in `note` what it needs.

Write with the snippet above, with your edit in place of the merge, keeping every field you did not
change:

```python
d = json.loads(text)
d["findings"]["R2"]["note"] = "The first fix is simpler: it moves one call."
print(json.dumps(d, indent=2))
```
