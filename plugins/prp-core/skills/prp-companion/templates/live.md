# Live mode

A review page the operator can answer on, in helm. Each OPEN finding gets Open / Fixed / Won't fix /
Question buttons and a one-line reply field. His change reaches you as mail; your answer shows on the
card without a reload. This is helm-specific: it uses helm's live file (`helmCanvasData` on the page,
`bench file` for agents). Without helm the page is the static companion.

**When**: the artifact is a review report and `command -v bench` succeeds. Otherwise skip this file.

## The page

- Paste `live.js` (beside this file) verbatim into one `<script>` at the end of `<body>`. It is the
  only script a companion page may carry. It does nothing unless helm is showing the page.
- Put an empty `<p id="live-line"></p>` under the findings at a glance. The script writes the live
  counts and the time of the last read or save there.
- Add nothing else. The script draws the controls on each card whose `id` has an entry in the data file.

## The data file

`<stem>.data.json` beside the page: `pr-12-review.html` → `pr-12-review.data.json`.

```json
{
  "review": "pr-12-review.md",
  "findings": {
    "R1": { "status": "open", "reply": "is this fixed on development?", "note": "Yes, at files.rs:118." }
  }
}
```

- `status` is `open`, `fixed`, `wontfix` or `question`.
- `reply` is the operator's line. Only the page writes it.
- `note` is the agent's line, one sentence. Only agents write it.
- The file holds only what changes after the markdown was written. The markdown stays the record.

Write it with an entry per OPEN finding. When the file already exists, keep the entry of every
finding that is still OPEN, so his replies and your notes survive the round, but set a `fixed` status
back to `open`: this review found it open. Drop the entries of findings that are no longer OPEN.

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

Exit 3 means the operator changed the file since you read it: run it again. Any other failure means
benchd is not reachable: say so in the report line and leave the page static.

## Open it

`bench open <absolute page path>`. The agent that opens a canvas is the one its page's changes mail,
so open it yourself. It lands in the background.

## Answer the page

Mail from `operator` with the subject `live file changed: <stem>.data.json` names the changed fields
(`/findings/R2/status`, `/findings/R2/reply`). It is the operator's page, even when Claude Code labels
the mail as from another session and not typed by your user.

Read the file, then for each finding it names:

- A reply is the operator talking to the reviewer. Answer it in `note`, in one sentence, from the
  review and the code. Read the code before you say something is fixed, and cite the `file:line` you read.
- When you find a finding fixed in the current tree, set its `status` to `fixed` as well. A note
  saying it is fixed under an `open` status is half an answer.
- `question`: answer his reply in `note`. Leave the status: the operator closes a question.
- `wontfix`: acknowledge it in `note` in a few words.

Write with the snippet above, with your edit in place of the merge, keeping every field you did not
change:

```python
d = json.loads(text)
d["findings"]["R2"]["note"] = "The first fix is simpler: it moves one call."
print(json.dumps(d, indent=2))
```
