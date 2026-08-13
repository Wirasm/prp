---
name: prp-debug
description: Diagnoses a bug, error, stack trace, regression, or unexplained behavior and publishes the evidence-backed root cause to GitHub. Use when the user says "debug this", "find the root cause", provides a bug report or stack trace, asks to investigate a GitHub issue, or invokes the prp-debug skill. Defaults to commenting on the matching open issue or creating one when none exists.
---

> **Kild lane:** you are running inside a kild room, in a workspace (worktree + branch) the kild engine assigned. The driver owns isolation and publishing — SKIP any step below that creates or switches branches or worktrees, pulls or rebases the base branch, pushes, opens PRs, or moves/archives plan artifacts, and never run `gh pr checkout`. Your job ends at implement → validate → commit in the current workspace, reporting evidence. Where a step spawns subagents, do that analysis inline — or ask the room's orchestrator to invite a helper agent.

> **Arguments:** `$ARGUMENTS` (and `$1`, `$2`, ...) refer to the arguments given when this skill was invoked. Take them from the user's request; if absent, infer them from the conversation.

# PRP Debug

Diagnose broken current behavior through the `root-cause-analyzer`, then make the finding durable in the appropriate GitHub issue. Do not implement the fix.

**Input**: $ARGUMENTS (if absent, use the conversation).

## 1. Resolve the report and publication target

Read repository guidance and establish the complete report: symptom, expected behavior, environment, reproduction, logs, and any supplied stack trace.

When the input points to a GitHub issue, read its body, relevant comments, linked issues, duplicates, pull requests, and attachments before diagnosing. Treat the body as historical context, not verified causality.

When no issue is specified, search open issues in the current GitHub repository using the symptom, distinctive errors, affected feature, and likely underlying behavior. Inspect candidate bodies and discussion; title similarity alone is not a duplicate.

- One clear match → use it.
- Several plausible matches → ask the user which issue should own the finding.
- No clear match → plan to create an issue after diagnosis.

If GitHub access or the repository cannot be resolved, complete the diagnosis but stop before publication and state what access is missing. Honor `--no-publish` or an equivalent explicit request without treating publication as a failure.

## 2. Run the root-cause analysis

Spawn `root-cause-analyzer` with the original report, complete tracker context, repository path, and any decisive runtime evidence already available. Do not give it a preferred cause or fix.

Require:

- reproduction at the cheapest authoritative boundary when reasonably possible;
- competing hypotheses and focused falsification;
- a causal chain from observed symptom to the smallest fixable cause;
- rejected alternatives and explicit uncertainty;
- the smallest responsible fix boundary;
- a regression check that fails before the fix and passes after it.

Do not publish a `UNRESOLVED` diagnosis as fact. Report the missing evidence and the next investigation step instead. Publish a `CONDITIONAL` diagnosis only with its condition prominent.

## 3. Reconcile duplicates with the diagnosis

For an unspecified issue, re-check the open candidates against the diagnosed behavior and cause. Reuse an issue only when it represents the same underlying problem, not merely a similar symptom.

If the diagnosis reveals that a supplied issue is a duplicate, comment on the issue the user supplied with the evidence and link the canonical open issue. Do not silently move the conversation elsewhere.

## 4. Publish the durable artifact

Unless publication was disabled or the current harness says its driver owns external publication:

- **Existing issue:** add a concise comment containing the corrected problem statement, reproduction evidence, root cause or explicit condition, causal chain, fix boundary, regression proof, and remaining uncertainty.
- **No matching issue:** create one with a concise problem-oriented title that states the observed impact and the same evidence as its body. Include expected and actual behavior and a reproducible procedure.
- **Wrong assumptions in an existing body:** correct them in the comment. Rewrite the body only when the user explicitly requests `--rewrite-body` or its natural-language equivalent; preserve still-useful original report details.

Do not create a separate local RCA document. The GitHub issue or comment is the artifact.

Read the created or updated issue back to verify the content and capture its URL. Report the diagnosis status, one-sentence cause, publication action, issue URL, fix boundary, regression proof, and any remaining uncertainty.
