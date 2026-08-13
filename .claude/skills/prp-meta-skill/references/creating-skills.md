# Creating a Skill (PRP-style)

Read `skill-standards.md` first. This runbook applies the PRP method to authoring a new skill.

## Step 1 — Gather context (Context is King)

Do not write anything yet. Collect, from the user or the codebase:

- **Triggers:** the exact phrases a user would say that should invoke this skill. Ask directly: "What would you type or say that should trigger this?" Capture 3–6 concrete phrases.
- **Task:** what the skill does, start to finish. What is the end artifact or output?
- **Gotchas & patterns:** non-obvious domain knowledge, existing patterns in the repo to mirror, constraints (the stuff a fresh agent would get wrong).
- **Scope boundary:** one skill = one capability. If two unrelated capabilities appear, that is two skills.

Ask the most important questions first; do not overwhelm with a long questionnaire.

Context is not only bundled. It can be **bundled** (`references/`/`templates/`), **external** (a repo file path or URL the skill cites), or **gathered at runtime** — and some skills are designed to collect context *when they run* (ask the user, read git/codebase, fetch a URL) rather than carry it. If so, that gathering is part of the skill's workflow; design it into Step 4. See `references/skill-standards.md` → Context sources.

## Step 2 — Plan the resources

For each part of the task, classify where it belongs (see `skill-standards.md`):

- Code rewritten every time, or needing deterministic reliability → `scripts/` (PEP 723 for Python).
- Reference detail that informs the work (schemas, API docs, exhaustive patterns, edge cases) → `references/`.
- A fixed output shape the result must follow → `templates/`.
- Files embedded/copied into the output (boilerplate, images) → `assets/`.
- Context you do not own or that changes upstream (third-party docs, specs) → cite by **file path or URL** in the body; do not bundle.
- Context that only exists at runtime (user intent, current repo state) → instruct the agent to **gather it** (ask the user, inspect the environment).

Write the list down before scaffolding. This is the skill's "implementation blueprint."

## Step 3 — Scaffold

```bash
mkdir -p .claude/skills/<name>
cp .claude/skills/prp-meta-skill/templates/SKILL.template.md .claude/skills/<name>/SKILL.md
# create references/ templates/ scripts/ assets/ only as the plan requires
```

Naming: `lowercase-hyphen`, descriptive, prefixed if part of a family (e.g. `prp-`). Directory name = the `/command`.

## Step 4 — Write the spine first (Progressive success)

Write `SKILL.md` to the standard:

- **Description:** third person, lead with what it does, then "Use when …" with the literal trigger phrases from Step 1. Include the `/name` invocation as one trigger.
- **Body (imperative):** the decision logic and workflow only. Each step is a verb-first instruction. Where a step needs bulk detail, write a one-line pointer to a reference instead of inlining it.
- **Invocation:** omit `user-invocable`/`disable-model-invocation` so an active PRP skill is both user- and agent-invocable. A deliberately manual experiment stays top-level for discovery, sets `disable-model-invocation: true`, is registered in `IN_PROCESS_SKILLS`, and is not distributed or called by compositions.
- End with a **Resources** section listing every bundled file.

Get this minimal version triggering and working before writing the references. A spine that does not trigger is worth more fixing than a perfect reference no one reaches.

## Step 5 — Fill the resources

Now write the planned `references/`/`templates/`/`scripts/`. Keep each focused. Apply no-duplication: as content moves into a reference, remove it from the body and leave a pointer.

For an output format the skill must ALWAYS follow, put the format in `templates/` and add a mandatory-read line in the body ("Before producing output, read `templates/<x>.md`"). For occasionally-needed detail, a lazy pointer is fine.

## Step 6 — Validate & iterate

Run every gate in `validation.md`: structure check, description quality, body style/length, progressive-disclosure check, the `plugin-dev:skill-reviewer` agent, and a real trigger test. Use the skill on a real task, watch where the agent struggles, and fold the fix back in. Strengthen triggers if it fails to auto-invoke; clarify or move content if the agent misuses it.

## From an existing command/prompt

**Fidelity first, optimize second.** Porting an existing, working command is a behavior-preservation task, not a redesign — land an identical-behaving skill and prove it *before* changing anything about how it reads. When the source is an existing slash command (the common PRP case):

1. Preserve the body **verbatim** — it is the proven process/output. Move it under `.claude/skills/<name>/SKILL.md`.
2. Transform only the frontmatter: add `name`, extend `description` with trigger phrases, keep `argument-hint`/`allowed-tools`/`model`.
3. Remove the old command file to avoid a duplicate `/name` registration.
4. If the body is long, hand off to `refactoring-skills.md` to split it — as a *separate* step, after the verbatim port is proven.
