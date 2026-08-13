---
name: <skill-name>
description: <What it does in one phrase>. Use when the user wants to "<trigger phrase 1>", "<trigger phrase 2>", "<trigger phrase 3>", or invokes /<skill-name>.
---

# <Skill Title>

<One or two sentences: the skill's purpose and the end artifact/output. Write in imperative voice from here on.>

<!-- The sections below are a STARTING SUGGESTION, not a required shape. Keep, drop, rename, or
     reorder them to fit this skill. A knowledge/reference skill may have no Workflow at all; a
     tool-wrapper may be mostly a Resources pointer. Decide your project's content yourself. -->

## When to use

<Briefly, the situations this applies to. Mirror the description's triggers.>

## Workflow

1. <Verb-first step.> <If a step needs bulk detail, point to a reference instead of inlining: see `references/<x>.md`.>
2. <Verb-first step.>
3. <Step that produces output.> Before producing output, read `templates/<output-format>.md` and follow it exactly.

## Gotchas

- <Non-obvious constraint the agent would otherwise get wrong.>

## Resources

- `references/<x>.md` — <when to read it>
- `templates/<output-format>.md` — <the required output shape>
- `scripts/<y>.py` — <what it does; run it, don't read it>

<!--
Authoring reminders (delete before shipping):
- description: third person + literal trigger phrases + /name. ≤1024 chars.
- body: imperative, the smallest complete decision spine. Detail → references/. Output shapes → templates/.
- match structure to the skill TYPE (workflow / artifact-generator / knowledge / tool-wrapper); don't force a workflow shape onto a knowledge skill.
- context can be bundled (references/templates), external (a file path or URL the body cites), or gathered from the user at runtime — pick per ownership/volatility.
- both user- and agent-invocable: do NOT set user-invocable/disable-model-invocation.
- wire every bundled file from the Resources section. No duplication body<->references.
- validate with references/validation.md and the plugin-dev:skill-reviewer agent.
-->
