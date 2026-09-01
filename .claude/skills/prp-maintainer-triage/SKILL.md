---
name: prp-maintainer-triage
description: Quickly triages a contributor pull request or reported issue against repository policy and lightweight evidence without full review or root-cause analysis. Use when the user asks to "triage this contributor PR", "sanity-check this PR", "triage this issue", "reproduce this reported issue", "check whether this bug still exists", or invokes /prp-maintainer-triage.
argument-hint: <issue-or-pr-number|url> [--no-publish]
disable-model-invocation: true
---

# Maintainer Triage

Resolve one GitHub pull request or issue, then load only its lightweight triage workflow.

**Input**: $ARGUMENTS (if absent, use the target named in the conversation).

Determine the target type from GitHub metadata, not keyword guesses. For a bare number, resolve a pull request with that number first, then an issue. If no single target can be resolved, ask the user which PR or issue to triage.

- **Pull request** — read `references/pr-triage.md` completely, then execute it end to end with the original input. Do not read the issue workflow.
- **Issue** — read `references/issue-triage.md` completely, then execute it end to end with the original input. Do not read the PR workflow.

Do not triage both kinds in one invocation or route into a heavier workflow.

## Resources

- `references/pr-triage.md` — lightweight contributor PR policy and reviewability triage
- `references/issue-triage.md` — lightweight issue reproduction and disposition
