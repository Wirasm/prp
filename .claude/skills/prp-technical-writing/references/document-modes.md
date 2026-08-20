# Document modes

Classify the unit being written before drafting. Use the whole document when writing a focused page,
or the requested section when working inside a mixed document such as a broad README. The mode answers
two questions: does the reader need to act or understand, and are they learning or doing real work?

| Reader need | Learning | Work |
|---|---|---|
| Act | Tutorial | How-to guide |
| Understand | Explanation | Reference |

Use the mode as a design choice, not a purity test. Keep a small example or table when it helps the
dominant purpose. Split and link when a second purpose needs its own sustained structure.

## Tutorial

Teach by helping the reader build something that works.

- Open with the concrete result the reader will produce.
- Make every step create visible progress, especially the first steps.
- State what the reader should see after important steps.
- Use direct commands and write as "we" when a shared learning path feels natural.
- Keep explanations short enough that they do not interrupt the lesson. Link to deeper explanation.

The tutorial owns the learner's success. Do not assume they can fill gaps that the lesson introduced.

## How-to guide

Help a competent reader complete a real task.

- Name the guide after the goal, not the underlying mechanism.
- Start close to the first useful action. Skip background the reader does not need.
- Put conditions before the steps they govern.
- Allow practical forks: "If the branch already exists, fetch it instead."
- Link to reference or explanation rather than interrupting the procedure.

A recommendation is useful when the reader must choose. State the trade-off briefly and continue.

## Reference

Make facts easy to find and trust.

- Mirror the structure and names of the system being described.
- State options, limits, defaults, return values, and errors without persuasion.
- Prefer generated material when an authoritative schema or source can produce it.
- Keep entries complete enough to use independently.
- Separate procedures and design arguments into linked documents.

Reference stays factual. Do not use it to sell the design or teach a journey.

## Explanation

Answer one bounded "why" question.

- Give the context that makes the design understandable.
- Explain constraints, decisions, alternatives, and consequences.
- Use evidence from the real system rather than generic software advice.
- Take a position when the evidence supports one. Do not flatten a decision into a neutral list.
- Keep procedures and exhaustive option lists in linked how-to or reference documents.

An explanation should still make sense when read away from the product UI or current task.
