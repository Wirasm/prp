---
name: prp-meta-skill
description: Authors, refactors, and consolidates Agent Skills PRP-style. Use when the user wants to "create a skill", "write a new skill", "trim a SKILL.md", "split a skill into references", "consolidate workflow skills", "replace duplicated skill logic with composition", redesign a skill workflow, or invokes /prp-meta-skill.
argument-hint: "[create <name> | refactor <path> | consolidate <skills...>] (blank = ask which)"
---

# PRP Meta-Skill — Author, Refactor & Consolidate Skills

A PRP-style runbook for three jobs:

- **Create** a new skill from scratch (or from an existing command/prompt).
- **Refactor** an existing skill — split detail into `references/`, move output formats into `templates/`, and trim `SKILL.md` to a lean spine of pointers.
- **Consolidate** overlapping workflows — trace their contracts, choose one composition owner, reuse specialist skills, and retire duplicate paths without losing outcomes or human gates.

This skill is built the way it teaches: a lean body that defers detail to `references/`. Follow that example.

## Prescribe the craft, not the content

This skill is opinionated about **how to build a skill well** and deliberately agnostic about **what any given skill — or the artifact it produces — should contain**.

- **Prescribe (firm, universal):** progressive disclosure, third-person trigger-rich descriptions, imperative body, no-duplication, lean body, every reference wired, deliberate invocation control, validation that fits. See `references/skill-standards.md`.
- **Do NOT prescribe (per-project, the author's call):** the sections a plan / PRD / report should contain, what a project's template looks like, which phases exist, the domain vocabulary. There is no canonical output shape — guide the author to a good decision, never hand them a fixed one.

Restrictions are not rigidity: be strict on the craft so the author stays free on the content.

## The PRP lens — applied to the skill *type*

Classify the skill first (workflow / artifact-generator / knowledge-reference / tool-wrapper — see `references/skill-standards.md` → Skill types), then apply only the principles that fit:

1. **Context is King** — give the agent ALL the context it needs (patterns, gotchas, schemas, examples) via whichever source fits: inline, bundled and disclosed on demand, pointed to by file path or URL, or gathered from the user at runtime. Curate it — don't dump it. (`references/skill-standards.md` → Context sources.)
2. **Validation that fits** — *workflow* skills ship verifiable gates, and prefer an external, authoritative check (exit code, file presence) over the agent's own "done" sentinel. A knowledge/reference skill has nothing to validate — don't bolt a loop onto it.
3. **Information dense** — real trigger phrases, real examples, real `file:line`. No filler, no restating what the model already knows.
4. **Progressive success** — ship the smallest complete SKILL.md that triggers correctly first, validate, then enrich with references. Don't build all the references before the spine works.

## Step 0 — Pick the mode

- **Creating** a new skill → follow `references/creating-skills.md`.
- **Refactoring / trimming** an existing skill → follow `references/refactoring-skills.md`.
- **Consolidating / redesigning** overlapping workflow skills → follow `references/consolidating-workflows.md`.
- All modes obey the same rules (frontmatter spec, writing style, progressive disclosure, no-duplication, invocation control) → read `references/skill-standards.md` first.

If the argument is blank, ask which mode and what the skill/target is. Do not guess.

## Create — quick spine (full detail in references/creating-skills.md)

1. **Gather context (PRP):** collect the concrete phrases that should trigger the skill, the task it performs, the gotchas, and existing patterns to mirror.
2. **Plan resources:** what repeats → a `scripts/` script; what informs thinking → a `references/` doc; what is reused in the output → a `templates/`/`assets/` file.
3. **Scaffold:** copy `templates/SKILL.template.md` into `.claude/skills/<name>/SKILL.md`; create `references/`, `templates/` only as needed.
4. **Write the spine:** third-person trigger-rich `description`; imperative, lean body; push detail to references.
5. **Validate & iterate** (`references/validation.md`): checklist → skill-reviewer → trigger test.

## Refactor — quick spine (full detail in references/refactoring-skills.md)

1. **Inventory** the target SKILL.md. Classify each block: _spine_ (keep) vs _extractable_ (output-format templates, schemas, long worked examples, exhaustive pattern catalogs, troubleshooting, edge-case lists).
2. **Extract verbatim** into the TARGET skill's own `references/` (or `templates/` for output formats). Do not reword anything that affects behavior.
3. **Replace with a pointer.** For **always-needed** content (e.g. an output format the agent must always follow), add a _mandatory-read_ instruction: "Before producing output, read `templates/<x>.md`." For **sometimes-needed** content, a lazy pointer ("For edge cases, see `references/<x>.md`").
4. **Behavior-preservation check** — the trimmed skill + references must drive the SAME process and SAME output as before. Nothing lost, nothing duplicated.
5. **Validate** (`references/validation.md`).

## Consolidate — quick spine (full detail in references/consolidating-workflows.md)

1. **Trace before editing.** Inventory inputs, callers, artifacts, side effects, publication, gates, correction paths, and every terminal outcome.
2. **Define the invariant.** Preserve the user-visible outcome and authoritative checks; distinguish intentional redesign from accidental regression.
3. **Assign ownership.** Give each phase, durable artifact, human decision, and retry loop one maintainer. Compose specialist skills by name instead of copying their instructions.
4. **Design handoffs.** Prefer semantic identifiers and complete durable artifacts over remembered filenames, parallel indexes, or lossy summaries. State when to preserve a context and when independence matters.
5. **Remove the old path.** Update every caller and public surface, regenerate derived targets, then exercise the new workflow end-to-end.

> The single biggest refactor risk: moving an _always-needed_ output format into a lazily-loaded reference, so the agent forgets to read it and the output silently changes. Always pair such extractions with a mandatory-read instruction. See `references/refactoring-skills.md`.

## Resources

- `references/skill-standards.md` — frontmatter spec, progressive disclosure, writing style, no-duplication, invocation control, cross-provider notes
- `references/creating-skills.md` — full PRP-style create runbook
- `references/refactoring-skills.md` — full split-and-trim runbook with a before/after example
- `references/consolidating-workflows.md` — workflow trace, ownership, context, publication, correction-loop, and retirement guidance
- `references/validation.md` — validation gates, checklist, skill-reviewer, trigger test
- `templates/SKILL.template.md` — lean SKILL.md skeleton
- `templates/reference.template.md` — skeleton for an extracted reference/template file
