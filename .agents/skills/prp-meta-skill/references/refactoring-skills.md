# Refactoring a Skill — Split & Trim

Read `skill-standards.md` first. Goal: take a fat `SKILL.md` and split detail into the skill's own `references/` and output formats into `templates/`, leaving a lean spine — **without changing what the skill does or outputs**.

## Golden rule

Behavior is sacred. Extraction relocates content; it must not change the process or the output. If you cannot guarantee a block is reproduced faithfully and still reached at the right time, leave it in the body.

## Step 1 — Inventory & classify

Read the whole target SKILL.md. Build a table of its blocks and classify each:

| Block | Type | Action |
|-------|------|--------|
| Purpose / when-to-use | spine | keep in body |
| Decision logic, phase/step workflow | spine | keep in body |
| Output / report format, document skeletons | **always-needed output** | → `templates/`, mandatory-read pointer |
| Schemas, data shapes, field tables | reference | → `references/`, lazy pointer |
| Long worked examples | reference | → `references/`, lazy pointer |
| Exhaustive pattern catalogs, "all the variations" | reference | → `references/`, lazy pointer |
| Troubleshooting, edge-case lists | reference | → `references/`, lazy pointer |

Spine = what the agent needs every run to know *what to do and in what order*. Everything bulky, output-shaped, or only-sometimes-needed is a candidate for extraction.

## Step 2 — Always-needed vs sometimes-needed (the critical distinction)

Progressive disclosure means a reference loads ONLY when the agent reaches for it. That is safe for sometimes-needed detail and dangerous for always-needed output formats.

- **Always-needed** (the output MUST follow it every time): extract to `templates/<x>.md`, and in the body add a **mandatory-read** instruction at the point of use:
  > Before producing the report, read `templates/report-format.md` and follow it exactly.
- **Sometimes-needed** (only under certain branches/edge cases): extract to `references/<x>.md` with a **lazy pointer**:
  > For conflict edge cases, see `references/edge-cases.md`.

Getting this wrong is the #1 way a refactor silently changes output: an output format moved to a lazy reference that the agent never loads.

## Step 3 — Extract verbatim

For each extracted block:

1. Create the destination file (`templates/` for output shapes, `references/` for detail) in the **target skill's own directory**, not the meta-skill's.
2. Move the content **verbatim**. Do not reword, re-order, or "improve" anything that affects behavior or output wording.
3. Give the file a short header naming what it is. Copy `templates/reference.template.md` from this meta-skill as the skeleton.

## Step 4 — Trim the body & wire pointers

In SKILL.md, replace each extracted block with its pointer (mandatory-read or lazy, per Step 2). Verify:

- The body still reads as a complete spine on its own.
- Every reference/template is linked from a "Resources" section.
- No content is duplicated between body and any reference (delete the original once moved).
- References are one level deep (linked directly from SKILL.md).

Aim the trimmed body at 1,500–2,000 words.

## Step 5 — Behavior-preservation check

Confirm the trimmed skill + resources is functionally identical to the original:

- Walk the workflow: at every point the original would have used the inlined content, the body now reaches the right pointer at the right time.
- The output format is still guaranteed (mandatory-read present for always-needed formats).
- Nothing was dropped in the move; nothing was duplicated.

If anything is uncertain, prefer keeping it in the body.

## Step 6 — Validate

Run `validation.md` gates, including the behavior-preservation gate and the `plugin-dev:skill-reviewer` agent.

---

## Before / after example (illustrative — prp-plan)

This shows **the technique, not a canonical plan shape.** What sections a plan contains is a per-project decision; the point here is only *how* extraction works, using a plan skill that happened to grow fat.

**Before:** `prp-plan/SKILL.md` inlines (a) the phase workflow, (b) the full plan-document skeleton it must emit, (c) detailed task-block guidance (MIRROR/IMPORTS/GOTCHA), and (d) a long list of per-language validation commands. ~3,000+ words, all loaded every run.

**After:**
```
prp-plan/
├── SKILL.md                       # spine: phases, decision logic, pointers (~1.5k words)
├── templates/
│   └── plan-document.md           # the plan skeleton — ALWAYS-needed output format
└── references/
    ├── task-block-format.md       # MIRROR/IMPORTS/GOTCHA detail (lazy)
    └── validation-commands.md     # per-language command catalog (lazy)
```
SKILL.md body keeps the Phase 0–5 workflow, and at the write-the-plan step says:
> Before writing the plan, read `templates/plan-document.md` and produce the document in that exact structure. For task-block detail see `references/task-block-format.md`; for the validation commands to embed, see `references/validation-commands.md`.

Same process, same plan output — but the body that loads every run is half the size, and the bulky catalogs load only when the planning step actually needs them.
