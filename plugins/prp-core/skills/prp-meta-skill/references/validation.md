# Validation Gates

Run these after creating, refactoring, or consolidating a skill. This is the PRP "validation loop" — fix failures before declaring done.

## Gate 1 — Structure

- `SKILL.md` exists with valid YAML frontmatter delimited by `---`.
- Frontmatter has `name` (matches directory, lowercase-hyphen, ≤64) and `description` (≤1024, non-empty).
- Every file referenced in the body actually exists (no dead pointers).

```bash
ls -R .claude/skills/<name>
grep -nE '`(references|templates|scripts|assets)/' .claude/skills/<name>/SKILL.md
```

## Gate 2 — Description quality (the trigger)

- For active skills: third person; not "Use this when you…"; states WHAT and WHEN; includes literal trigger phrases and the `/name` invocation. A skill that acts on the conversation itself is user-only by design: expect `disable-model-invocation: true` and no trigger phrases.
- `user-invocable` and `disable-model-invocation` are NOT set, unless invocation control was a deliberate decision under `skill-standards.md`. For an in-process experiment registered in `PLUGIN_EXCLUDED_SKILLS`, verify it is authored in this repository's `.claude` skill source tree, its description is only `This is an experimental skill. Never use it unless the user explicitly tells you to invoke /<name>.`, explicit user and agent invocation work, it is absent from the public plugin and from active composition callers, and its Codex render exists so the author can exercise it.

## Gate 3 — Body style & size

- Imperative/infinitive voice throughout; no second person ("you should").
- Body is the decision spine + pointers, not a data dump.
- Use the smallest complete decision spine; investigate anything approaching ~5k words.

## Gate 4 — Progressive disclosure

- Bulky / occasionally-needed / output-shaped detail lives in `references/` or `templates/` (or is cited by file path / URL, or gathered at runtime), not inlined in the body.
- No content duplicated between body and resources.
- Always-needed output formats have a **mandatory-read** pointer; sometimes-needed detail has a lazy pointer.
- References are one level deep and all linked from a Resources section.

## Gate 5 — Fidelity or intentional redesign

- For a fidelity refactor, the trimmed skill + resources drives the SAME process and output; every moved block remains reachable at the right time.
- For consolidation, the new outcome and invariants are explicit; every old input, side effect, publication, gate, correction path, and terminal outcome is either preserved or deliberately retired.
- Every phase and stateful artifact has one owner. Cross-context handoffs use complete durable artifacts and semantic identity, not lossy summaries or remembered filenames.
- Human-facing decisions have a verified human-visible publication. Independent review or validation reruns after corrections.
- All callers and public surfaces use the new owner; removed skills and obsolete artifact contracts are absent after regeneration.

## Gate 6 — Skill-reviewer agent

Run the dedicated reviewer for an independent check of description quality, organization, and progressive disclosure:

> Use the `plugin-dev:skill-reviewer` agent to review `.claude/skills/<name>` against skill best practices.

If that agent is unavailable, run Gates 1–5 manually as the equivalent check.

Apply its high-confidence findings; ignore noise.

## Gate 7 — Trigger test, then exercise for real

- **User invocation:** confirm `/<name>` appears and runs.
- **Agent invocation:** describe a task in the skill's domain (using one of the trigger phrases) and confirm the skill auto-loads. If it does not, strengthen the `description` triggers and retry.
- **Exercise it end-to-end on a real task** — don't stop at "it loaded." Run the skill against actual work and watch it execute; a real run surfaces bugs a load-check never will (a real end-to-end run is how the prp-loop caught a defect in its own commit logic). Fold what you learn back in.

## Done criteria

All seven gates pass. Gate 5 is non-negotiable: fidelity work may not drift, and intentional redesign must prove the replacement contract rather than hiding behavior loss as cleanup.
