# Contributing

Thanks for your interest in PRPs-agentic-eng.

## A note on scope and expectations (please read first)

Up front, so it's clear: **this repo is my personal agentic-engineering workflow** — my prompts, my skills, my way of working. I use it on essentially every project I actively develop, which means the skills here are *load-bearing* to my daily work.

You are very welcome to:

- Use it, fork it, and adapt it to your own workflow
- Open issues and ideate — discussion and ideas are genuinely appreciated
- Send pull requests

But please know up front that **I'm deliberately picky about what I merge.** Because these skills run my real projects, I won't accept changes that risk destabilizing that workflow — however good they are in the abstract. If a PR isn't merged, it's usually not a judgment on its quality; it's that I keep this surface small and stable on purpose. Often the best way to extend the framework for *your* needs is to copy the pieces you want into your own `.claude/` and shape them there.

## How the repo is structured

- **`.claude/skills/`** — the PRP skills (the working source). Each is a self-contained Agent Skill: a `SKILL.md` plus optional `references/`, `templates/`, and `scripts/`.
- **`plugins/prp-core/`** — the same skills packaged as a distributable Claude Code plugin. Its `skills/` and `agents/` are generated from `.claude/` by `scripts/sync_plugin.py` — edit the `.claude/` source, then regenerate; never edit the plugin copies directly.
- **`old-prp-commands/`** — the previous slash-command generation, kept for reference.
- **`claude_md_files/`** — framework-specific `CLAUDE.md` examples.
- **`PRPs/templates/`, `PRPs/ai_docs/`** — templates and curated documentation.

## Authoring skills

The framework documents its own conventions — use the **`prp-meta-skill`** (`/prp-core:prp-meta-skill`) to author or refactor a skill. In short:

- Lean `SKILL.md` (the decision spine); detail in `references/`; output shapes in `templates/`.
- Third-person, trigger-rich `description`; imperative body.
- **Prescribe the craft, not your project's content** — there's no canonical template; that's a per-project decision.
- Keep each skill self-contained (no cross-skill file references).

## Conventions

- **Commits:** conventional style (`feat(scope): …`, `fix(scope): …`, `refactor(scope): …`, `docs(scope): …`), written as a human would — no AI attribution.
- **Branches:** work on a feature branch. The default branches are `main` and `development`, kept in sync.
- **Validation:** skills are markdown; the bundled `prp_loop.py` should pass `python3 -m py_compile`, and `python3 scripts/sync_plugin.py --check` must pass. Run any relevant project checks before opening a PR.

## Submitting a PR

1. Keep it focused — one capability or fix per PR.
2. Mirror the existing skill structure and conventions.
3. Explain what changed and why; reference any related issue.
4. Expect questions, and expect load-bearing changes to get extra scrutiny.

Thanks for understanding — and for building on this.
