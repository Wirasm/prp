# Sentence style

Write for a tired engineer who should understand the text on the first read. The rules serve that
reader. When a mechanical application makes a sentence worse, rewrite another way or leave it alone.

## Use plain, concrete language

- Cut every word that does no work. "In order to" becomes "To." Delete "It is important to note that."
- Prefer the short accurate word. Use "use", not "utilize"; "help", not "facilitate."
- Name the mechanism, symbol, command, or measurement. "Schema changes can cause issues" becomes "A
  column rename fails the build."
- Keep one established name for each thing. Do not rotate synonyms merely to vary the prose.
- Preserve precise project terms. Remove invented jargon and abstract metaphors, not useful domain
  language.
- Name the source of a claim. Replace "experts believe" with evidence or delete it.

## Address the reader and the action

- Use "you" and present tense when addressing the reader.
- Write instructions as commands. Put the condition before the instruction it guards.
- Put the common path first and exceptions after it.
- Prefer active voice when the actor matters. Passive voice is fine when the actor is unknown or
  irrelevant.
- Never call a procedure "simple", "easy", or "quick". Give the reader the steps and evidence instead.
- Use the codebase as the word list. Write the real file, flag, type, or UI label.

## Keep one reading

- Give each sentence one action or one thought. Keep a longer sentence when every clause supports the
  same thought.
- Put "only", "not", and other modifiers next to the words they change.
- Make every "it", "they", and "this" point to one obvious noun. Repeat the noun when needed.
- Break long noun strings into clauses: "the proto import budget check script" becomes "the script
  that checks the proto-import budget."
- Keep articles and verbs when omitting them would make the sentence ambiguous.
- Spell out relationships in prose. Use "a, b, or both" instead of "a/b" or "and/or."

## Sound human

- Vary sentence length. Short sentences land a point. Longer sentences can carry one fact with its
  condition or consequence.
- State a view when the document mode allows it. Do not manufacture neutral pros-and-cons lists.
- Use first person when it clarifies whose judgment or experience is being reported.
- Remove puffery, promotional language, forced groups of three, generic conclusions, excessive
  hedging, and superficial "-ing" phrases.
- Remove chatbot phrases such as "Great question!", "Of course!", and "I hope this helps!"
- Prefer specifics over sterile prose. If a sentence could appear unchanged in another project's
  documentation, make it concrete or cut it.

## Format without decoration

- Use sentence-case headings with one `#` heading per page and no skipped levels.
- Use numbered lists for sequences and bullets for other lists. Introduce each list with a complete
  sentence and keep its items parallel.
- Put code, paths, flags, and symbols in code formatting. Use the product's convention for UI labels.
- Use descriptive link text, not "click here."
- Avoid decorative emoji, excessive bold labels, curly quotes, em dashes, and semicolons.

## Worked edit

Before:

> Configuration of the proto import ratchet budget script parameters is performed via budget.json.
> Note that it is important to remember that running with --write, which updates the committed budget
> to reflect the current count, should only be done when lowering it. If exceeded, CI fails.

After:

> `budget.mjs` reads the committed budget from `budget.json` and counts the files that import protos.
> If the count exceeds the budget, CI fails. Run `budget.mjs --write` only to lower the budget.

The edit names the actor and the real files, removes filler and metaphor, puts the failure condition
before the command, and moves "only" next to the action it limits.

## Final pass

Check that:

1. Every instruction is direct and its condition comes first.
2. Every sentence carries one clear thought and every pronoun has one referent.
3. Every concept has one name, preferably the repository's real name.
4. Every symbol, path, command, link, count, and expected result is true at this revision.
5. No word can be cut without losing meaning or tone.
6. The rhythm varies and the prose has a view where the document mode allows one.
7. No filler, vague claim, promotional phrase, or chatbot opening remains.
