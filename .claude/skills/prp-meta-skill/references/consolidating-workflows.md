# Consolidating Workflow Skills

Use this mode when the requested change intentionally replaces overlapping processes with one composition. This is not a fidelity-only refactor: preserve the required outcome and invariants, while allowing duplicated mechanics and obsolete artifacts to disappear.

## 1. Trace the current contracts

Read every active skill, caller, reference, template, script, and public description involved. Ignore generated copies and retired sources except as migration evidence.

Map:

- accepted inputs and how each is resolved;
- phase order and the owner of each phase;
- artifacts written, their source metadata, and downstream consumers;
- external side effects and authoritative verification;
- human-visible publications and decision gates;
- context boundaries and what crosses them;
- correction, retry, and resume paths;
- success, no-op, recoverable blocker, and failure terminals.

Write the trace before proposing the replacement. A workflow understood only as its happy-path arrows will lose behavior at the seams.

## 2. State the replacement contract

Name the observable outcome and invariants that survive the redesign. Separately list machinery that is intentionally retired. Do not call an intentional behavior change a behavior-preserving refactor.

Prefer one composition owner for the end-to-end outcome and one specialist owner per phase. The composition skill routes, gates, and carries references; it does not copy the planning, implementation, publishing, or review craft owned elsewhere.

Remove a superseded skill completely when compatibility is not required. A thin alias still creates a second trigger, concept, and maintenance surface.

## 3. Design durable handoffs

Every context transition needs a complete contract. Pass the authoritative artifact itself plus stable identity and live external state—not a prose recollection of it.

Use semantic discovery such as source issue, plan ID, branch, or PR number. Avoid making future users remember generated filenames. Prefer scanning source metadata over adding a separate index that another step must maintain. If more than one candidate matches, surface the candidates rather than guessing.

When an artifact must be useful to humans or collaborators outside the local agent session, publish it on the system where the decision happens and verify the publication. Keep the local artifact as the durable agent handoff and store the stable publication URL in its metadata. Link that public artifact from downstream public artifacts.

Never reduce a rich upstream contract to a private boolean or one-line list when downstream work needs its evidence, attribution, validation, or decisions.

## 4. Choose context boundaries deliberately

Keep one context when it owns an execution lifecycle and accumulated reasoning materially helps the next action. Resume that owner for corrections when the harness permits it.

Use an independent context when independence is the feature, such as reviewing implementation. A fresh fallback context must reconstruct the full contract from durable artifacts and live state.

Put human decisions between judgment and mutation. Publish the evidence first, then pause unless an explicit standing decision authorizes the composition to proceed. Feed the human's dispositions back to the execution owner and re-run independent validation or review after changes.

## 5. Assign maintainers and terminal outcomes

For every stateful field, report, comment, status, or loop, name the step that creates it and the step that updates it. Prefer updating one current-truth artifact over producing competing summaries, unless immutable history is itself required.

Define all terminals:

- completed outcome and its authoritative proof;
- human decision required and the artifact they read;
- recoverable blocker with preserved state and resumption input;
- incomplete validation or evidence;
- exhausted autonomous safety bound;
- no-op such as an already-existing external artifact.

Do not let bounded autonomous execution silently weaken an interactive human gate. Treat detached automation as an explicit mode with its own persisted state and safety policy.

## 6. Retire and validate

Update active callers, trigger descriptions, examples, templates, documentation, generated distributions, and state/artifact descriptions. Search for the retired skill name and obsolete artifact contract after regeneration.

Validate both structure and behavior:

1. Walk each traced input through the new phases.
2. Verify every handoff can be recovered in a fresh context.
3. Verify human-facing artifacts appear in the external system and are linked downstream.
4. Exercise a correction or retry loop with the complete upstream artifact.
5. Test success, human gate, blocker, and no-op terminals.
6. Run authoritative scripts and distribution-sync checks.
7. Exercise the composition on real work before declaring the old path retired.
