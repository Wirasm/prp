---
name: prp-technical-writing
description: Writes and edits developer documentation that is easy to act on and hard to misread. Use when writing or reviewing a README, RFC, tutorial, how-to guide, reference document, or technical explanation, when the operator says "write the docs", "improve this README", "edit this RFC", or invokes $prp-technical-writing.
---

> **Arguments:** `$ARGUMENTS` (and `$1`, `$2`, ...) refer to the arguments given when this skill was invoked. Take them from the user's request; if absent, infer them from the conversation.

# Write technical documentation

Write or edit substantial developer documentation for the intended reader and task.

**Input**: $ARGUMENTS

## Scope

Treat requests to review, critique, or answer a question as read-only. Edit files only when the
operator asks for a change.

Leave product UI copy to the product's copy rules. Leave ordinary commit messages and pull request
descriptions to `$prp-commit` and `$prp-pr` unless the operator explicitly invokes this skill for an
editorial pass.

## 1. Establish the source of truth

Read the repository guidance, requested draft, relevant source, and existing documentation before
writing. Identify the reader, the action or understanding they need, and the authoritative sources
for the document's claims.

Use the repository's real symbols, paths, flags, commands, and product terms. Do not invent behavior,
results, measurements, or terminology to make the prose sound complete.

## 2. Choose the document mode

Before drafting, read `references/document-modes.md`. Choose the dominant mode for the unit the
operator asked to write: the whole document, or one focused section within a mixed document. Split
and link when a competing mode becomes substantial; do not split a useful example or small reference
table merely for structural purity.

## 3. Write for the first read

Before writing or editing, read `references/sentence-style.md`. Use direct, concrete language and a
natural rhythm. Preserve precise domain terms, but remove filler, invented metaphors, vague claims,
and formulaic AI phrasing.

Organize the document around the reader's task or question. Keep background only when it changes what
the reader understands or does.

## 4. Prove the document

Check every named symbol, path, flag, link, count, command, and expected result against the real
source. Run examples and commands when doing so is safe and relevant. Otherwise state what remains
unverified instead of presenting it as fact.

Confirm that procedures follow the actual user path and that reference material matches the
authoritative implementation or schema.

## 5. Edit once more

Remove words that do no work. Resolve ambiguous pronouns, modifiers, and overloaded names. Split any
sentence that makes the reader backtrack.

Ask, "What makes this sound generated?" Rewrite the remaining tells without making the prose sterile
or changing its meaning.

## Handoff

Report the documents reviewed or changed and the evidence used to verify them. Do not commit or open
a pull request unless the operator asks.

## Resources

- `references/document-modes.md` — choose and shape tutorials, how-to guides, reference, and explanation
- `references/sentence-style.md` — write plain, precise sentences and remove generated-sounding prose
