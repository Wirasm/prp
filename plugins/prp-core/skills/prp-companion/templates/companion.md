# Companion page

One HTML page that shows a plan or a review to a human faster than the markdown does. The markdown
stays the artifact. The page is derived from it and states nothing the markdown does not.

## The file

- One self-contained `.html` file. Nothing on the page is loaded from a network: no CDN script,
  no web font, no remote image, no `@import`, no `fetch`. Draw every visual as inline SVG. Add no
  JavaScript; native `<details>` covers collapsing.
- The theme is the first `<style>` block, pasted verbatim (see `SKILL.md` for which file). Spend
  colour and font only through its custom properties: `--surface`, `--raised`, `--text`, `--muted`,
  `--faint`, `--border`, `--accent`, `--attention`, `--danger`, `--font-body`, `--font-mono`. No
  colour literal anywhere else, so the page follows the theme in light and dark.
- Layout: body on `--surface`, max width about 60rem, 15px text, section labels small caps in
  `--faint`, code and paths in `--font-mono`. Cards on `--raised` with a `--border` outline. Give
  every card `overflow-wrap: anywhere` so a long path or test name wraps instead of overflowing.
- Foot line: the markdown's filename, and that evidence, commands and file lists are there.

## Rules for every page

- **Words.** The page exists so the human reads less. Aim for at most a third of the markdown's
  words. Prefer a diagram, a table row or a chip to a sentence. Evidence, commands, file lists and
  alternatives stay in the markdown.
- **The three things first**, in the order given below for the artifact kind. The first screen
  answers "what is this and what do I have to decide".
- **Copy, never paraphrase.** Risk text, finding text, required outcomes, acceptance criteria, the
  plan's outcome and the review's opening paragraph are the markdown's words, copied whole. So are
  file paths, `file:line`, severities, states, counts, verdicts and step titles. Shorten by leaving
  a field out, never by rewording it. Never merge table cells into a new sentence: a card built from
  a table row shows each cell as it is, under its column name. A certainty in the markdown stays a
  certainty on the page. No sentence adds a judgement the markdown did not make.
- **Every item carries a stable `id`** on the element that wraps the whole item, and nowhere
  decorative. A mark a human makes on the page resolves to the nearest ancestor `id`, so the id is
  how the author learns which item was meant. Use the markdown's own identifiers where it has them:

  | Item | id |
  |---|---|
  | plan step | `S1`, `S2`, … in plan order |
  | plan risk or decision | `K1`, `K2`, … |
  | acceptance criterion | its own id, `AC1`, … |
  | diagram component | `C-<slug>` |
  | review finding | its report ID, `R1`, … |

- **Diagrams** are inline SVG with real `<text>` labels, so a label can be marked. Each node that
  stands for an item carries that item's id on its `<g>`. Draw only relationships the markdown
  states. No label on an edge: the arrow's direction and the two boxes say enough, and an edge label
  always ends up sitting on a line or crossing a box. Route edges orthogonally around boxes. Size
  each box to its text, or split the text over two `<tspan>` lines. Mark new, changed and unchanged
  elements with `--accent`, `--attention` and `--border`, and say so in a one-line legend.

## Plan page

Header: plan title, plan ID, and the source issue reference. Leave out the markdown's metadata labels
(`Plan ID:`, `Source Issue:`): skills find plans by grepping those lines, and the page is not a plan.

The three things, in this order:

1. **What changes.** A diagram of the components the plan touches and how they connect after the
   change: new, changed, unchanged. Under it, the plan's **Approach** copied.
2. **The steps.** One card per implementation task (`id="S<n>"`): its title, and the files or
   components it touches by short name. Mark the step that carries the first test or the riskiest
   change, when the plan says which.
3. **The risks.** One card per row of **Risks and Decisions** and per row of **Delivery
   Considerations** (`id="K<n>"`), cells copied under their column names. Only rows the plan puts in
   those sections are risks. **Not building** is never a risk card: show it as one quiet line of its
   items in `--muted`, below the risk cards.

Then, smaller: acceptance criteria (`id="AC<n>"`, text copied), and the validation gates as a table
of gate and what it proves.

## Review page

Header: `PR <number> review`, head branch → base, reviewed head short SHA and timestamp.

The three things, in this order:

1. **The verdict** as a large chip: `--accent` for READY TO MERGE, `--attention` for NEEDS FIXES,
   `--danger` for REVIEW INCOMPLETE. Beside it the blocking and non-blocking counts. Under it, the
   report's opening paragraph, copied whole: it says what was checked and why the verdict follows.
   Then the **Validation** line.
2. **The findings at a glance.** A bar or row of counts per severity, and a count per state.
3. **The findings.** OPEN findings first, by severity (Critical, Important, Suggestion) then ID. Each
   is a card (`id="R<n>"`): severity chip, state chip, the finding line, `file:line` in mono, and the
   required outcome. Impact, evidence, class and disposition go in a closed `<details>` inside the
   card, copied. After the OPEN ones, every other finding (FIXED, NOT A FINDING, TRACKED FOLLOW-UP,
   DECLINED) by ID as one line each, still wrapped in its `id`: chips and the finding line, with its
   disposition in a closed `<details>`.

Then, smaller: reviewer coverage (scope → result). A review with no findings still shows the verdict,
the opening paragraph and the line "No findings."
