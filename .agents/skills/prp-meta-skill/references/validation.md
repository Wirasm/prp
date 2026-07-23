# Validation Gates

Run these after creating or refactoring a skill. This is the PRP "validation loop" — fix failures before declaring done.

## Gate 1 — Structure

- `SKILL.md` exists with valid YAML frontmatter delimited by `---`.
- Frontmatter has `name` (matches directory, lowercase-hyphen, ≤64) and `description` (≤1024, non-empty).
- Every file referenced in the body actually exists (no dead pointers).

```bash
ls -R .agents/skills/<name>
grep -nE '`(references|templates|scripts|assets)/' .agents/skills/<name>/SKILL.md
```

## Gate 2 — Description quality (the trigger)

- Third person; not "Use this when you…".
- States WHAT it does AND WHEN to use it.
- Contains literal trigger phrases a user would actually say, plus the `/name` invocation.
- For PRP family: `user-invocable` and `disable-model-invocation` are NOT set (both invocation paths stay open).

## Gate 3 — Body style & size

- Imperative/infinitive voice throughout; no second person ("you should").
- Body is the decision spine + pointers, not a data dump.
- Target 1,500–2,000 words; investigate anything over ~5k.

## Gate 4 — Progressive disclosure

- Bulky / occasionally-needed / output-shaped detail lives in `references/` or `templates/` (or is cited by file path / URL, or gathered at runtime), not inlined in the body.
- No content duplicated between body and resources.
- Always-needed output formats have a **mandatory-read** pointer; sometimes-needed detail has a lazy pointer.
- References are one level deep and all linked from a Resources section.

## Gate 5 — Behavior preservation (refactors only)

- The trimmed skill + resources drives the SAME process and SAME output as the original.
- At every point the original used inlined content, the body now reaches the right pointer at the right time.
- Nothing dropped, nothing duplicated. When uncertain, keep content in the body.

## Gate 6 — Skill-reviewer agent

Run the dedicated reviewer for an independent check of description quality, organization, and progressive disclosure:

> Use the `plugin-dev:skill-reviewer` agent to review `.agents/skills/<name>` against skill best practices.

If that agent is unavailable, run Gates 1–5 manually as the equivalent check.

Apply its high-confidence findings; ignore noise.

## Gate 7 — Trigger test, then exercise for real

- **User invocation:** confirm `/<name>` appears and runs.
- **Agent invocation:** describe a task in the skill's domain (using one of the trigger phrases) and confirm the skill auto-loads. If it does not, strengthen the `description` triggers and retry.
- **Exercise it end-to-end on a real task** — don't stop at "it loaded." Run the skill against actual work and watch it execute; a real run surfaces bugs a load-check never will (a real end-to-end run is how the prp-loop caught a defect in its own commit logic). Fold what you learn back in.

## Done criteria

All seven gates pass. For a refactor, Gate 5 is non-negotiable: a refactor that changes output is a regression, not a cleanup.
