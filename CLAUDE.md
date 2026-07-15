# CLAUDE.md

Guidance for Claude when working **on this repository** — what it is, the philosophy behind it, and how to improve its skills and assets.

## What this repo is

A personal **PRP (Product Requirement Prompt) framework** — an agentic-engineering workflow packaged as Claude Code **Agent Skills**. It is not an application: its "source" is *prompts and assets* — skills, agents, templates, and curated docs.

**PRP = PRD + curated codebase intelligence + agent/runbook** — the minimum context an AI needs to ship a vertical slice of working software in one pass.

This framework is **load-bearing**: it's used on real, active projects every day. Treat changes accordingly — preserve behavior, stay conservative, and don't destabilize working skills for the sake of elegance.

## Philosophy

The principles that govern everything here:

- **Context is King** — give the agent all the context it needs (inline, in references, or fetched at runtime), curated, never dumped.
- **Validation loops** — workflow skills ship executable gates the agent loops on until green; prefer an authoritative external check over a self-reported "done."
- **Information dense** — real patterns, real `file:line`, real commands; no filler, no restating what the model already knows.
- **Progressive success** — ship the lean spine first, validate, then enrich.
- **Prescribe the craft, not the content** — be strict on *how* a skill is built; stay agnostic about *what* a given skill or its output should contain (that's per-project, the author's call). The one deliberate escape hatch is a free-form "Agent Notes" canvas.
- **One source of truth** — a skill lives in one place; if it must exist in two, generate/sync one from the other rather than hand-maintaining both.
- **Structure implies a maintainer** — never add a stateful section (status markers, lifecycle, amendments) that nothing keeps current.
- **Fidelity first** — when porting or refactoring, preserve behavior exactly and prove it, *then* optimize.

## What lives where

- **`.claude/skills/`** — the skills, and the working **source of truth**. Each is a self-contained Agent Skill: a `SKILL.md` spine plus optional `references/`, `templates/`, `scripts/`.
- **`plugins/prp-core/`** — the same skills + agents (+ plugin-only hooks) packaged as a distributable plugin. Its `skills/` and `agents/` are **generated from `.claude/` by `scripts/sync_plugin.py`** — never edit them directly; edit the `.claude/` source and regenerate. The script owns the intentional differences: the `prp-loop` launcher path (`.claude/PRPs/scripts/prp_loop.py` → `${CLAUDE_PLUGIN_ROOT}/skills/prp-loop/scripts/prp_loop.py`), bundling `prp_loop.py` into the skill, and excluding personal agents (`gpui-researcher`). `hooks/`, `README.md`, and `.claude-plugin/` are plugin-only and hand-maintained.
- **`.claude/agents/`, `plugins/prp-core/agents/`** — advisory (read-only) review/research subagents.
- **`claude_md_files/`** — framework-specific `CLAUDE.md` examples (Rust, Python, Node, React, …).
- **`PRPs/templates/`, `PRPs/ai_docs/`** — PRP templates and curated reference docs.
- **`old-prp-commands/`** — the retired slash-command generation. **Reference only — do not maintain or extend it.**

## How to improve skills and assets

1. **Author or refactor with `prp-meta-skill`** (`/prp-core:prp-meta-skill`). It encodes the craft: lean `SKILL.md`, detail in `references/`, output shapes in `templates/`, a third-person trigger-rich `description`, an imperative body, no duplication, and self-containment (no cross-skill file references).
2. **Classify the skill type** (workflow / artifact-generator / knowledge / tool-wrapper) and apply only the principles that fit — don't force phases or validation loops onto a knowledge skill.
3. **Regenerate the plugin** whenever you touch a skill or agent: `python3 scripts/sync_plugin.py` (verify with `--check`).
4. **Bundled scripts must be location-agnostic** — derive the project root from git/cwd, never from `__file__`; the script operates on the user's project, not the skill directory.
5. **Validate the change**: skills are markdown (nothing to build); `prp_loop.py` must pass `python3 -m py_compile`; `python3 scripts/sync_plugin.py --check` must pass; the real test is triggering the skill and exercising it end-to-end.

## Conventions

- **Agent naming:** skills always reference the pack's subagents with the plugin namespace — `prp-core:code-reviewer`, `prp-core:codebase-explorer`, … — never bare names. This assumes the prp-core plugin is enabled wherever the skills run (including this repo).
- **Commits & PRs:** conventional style (`feat(prp-core): …`, `refactor(…): …`), written as a human would — no AI attribution, no `Co-Authored-By: Claude`.
- **Branches:** work on a feature branch; `main` and `development` are the primary branches and are kept in sync.
- **Contributing:** see `CONTRIBUTING.md` — changes are scrutinized because the skills are load-bearing.

## Don't

- Don't treat this as an application — there are no app build/test/deploy gates to add here.
- Don't maintain or extend `old-prp-commands/`.
- Don't break a working skill's behavior for a refactor — fidelity first.
- Don't add cross-skill file references — it breaks self-containment and the plugin sync.
