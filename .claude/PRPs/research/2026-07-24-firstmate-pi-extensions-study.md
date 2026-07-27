# Study: firstmate's `.pi/extensions/` (Pi harness adapter layer)

**Source:** https://github.com/kunchenguid/firstmate/tree/main/.pi/extensions (studied at commit `f017572`, 2026-07-23)
**Studied:** 2026-07-24

## What firstmate is (context)

firstmate is an **"agent distro"** — no app, no CLI, no MCP server. The cloned repo *is* the product: `AGENTS.md` + bundled skills + ~90 bash scripts + state conventions that turn any terminal coding agent into a fleet orchestrator (the "first mate"). You talk to one agent; it spawns crewmates into tmux/herdr/zellij/cmux/orca windows, each in a disposable [treehouse](https://github.com/kunchenguid/treehouse) worktree, and supervises them to PRs/merges/reports.

It supports **five primary harnesses** — Claude Code, Codex CLI, OpenCode, Pi, Grok — with one shared bash core and a thin per-harness adapter for each. `.pi/extensions/` is the **Pi adapter** (Pi = `@earendil-works/pi-coding-agent`, Mario Zechner's pi; auto-loads `.pi/extensions/*.ts` from a trusted project, or explicitly via `pi -e <file>`).

The layer is ~1,250 lines of strict TypeScript across 7 files: three extensions + four shared libs.

## The three extensions

### 1. `fm-primary-turnend-guard.ts` (162 lines) — lifecycle safety backstop

One file deliberately carries three duties so Pi only needs to load a single extension:

- **Session-start nudge** — on `session_start` with reason `startup|new|resume`, runs `bin/fm-sessionstart-nudge.sh` and injects the output via `pi.sendMessage({customType, content, display: false})`: enters model context invisibly, without racing an initial positional prompt.
- **PreToolUse seatbelts** — `pi.on("tool_call")` on `bash` commands shells out to `fm-cd-pretool-check.sh` (cd-guard) and `fm-arm-pretool-check.sh` (never run the watcher-arm script via bash). Exit code 2 → return `{block: true, reason: stderr}` — verified against pi 0.80.5+ that returning `{block: true}` actually prevents execution.
- **"No turn ends blind" guard** — on `agent_settled`, runs the shared predicate `bin/fm-turnend-guard.sh` (in-flight tasks counted from `state/*.meta` + no identity-matched live watcher with fresh beacon → exit 2). Pi has no blocking Stop hook (unlike Claude/Codex), so the adapter instead **forces one follow-up turn**: `pi.sendUserMessage(content, {deliverAs: "followUp"})`. An in-process latch (`guardFollowupActive`) prevents the forced follow-up from recursively re-triggering the guard; delivery failure clears the latch and fails open.

Also writes a marker file (`state/.pi-turnend-extension-loaded`) containing `sha256(extension file)` + pid, so session-start checks can verify the *loaded* extension matches the *tracked* one.

### 2. `fm-primary-pi-watch.ts` (470 lines) — zero-token supervision bridge

The heart of "event-driven, zero-token supervision." The bash watcher (`bin/fm-watch-arm.sh --restart`) is deliberately **one-shot**: it sleeps on fleet state and exits with one actionable reason. This extension owns *continuity* above that process boundary, so re-arming never depends on the model remembering to do it:

- **Spawn & classify** — spawns the arm script as a child (through `bash -lc` that sources `config/x-mode.env` first). On close, classifies output: a line matching `^(signal:|stale:|check:|heartbeat)` is *actionable*; a `watcher: healthy` line from the arm child is itself a **failure** (the child found an external watcher instead of owning wake delivery); everything else is a typed failure.
- **Successor-before-wake ("Option B") ordering** — after an actionable close, it starts and *verifies* a singleton successor watcher **before** delivering the wake prompt to the model. Readiness = observing `watcher: started|attached` on the child's stdio within 12s. An unready successor gets SIGTERM + a bounded 1s retirement wait before the next retry. Bounded exponential retry: 250ms → 4s cap, 5 attempts. If everything fails, the original wake is still delivered with a typed continuity-restoration failure appended — the fleet is protected when possible, the model is never left blind.
- **Lock-ownership check** — reads `state/.lock` (a pid), then walks its own ppid chain up to 8 hops via `ps -o ppid=` to decide `owned | missing | other`. Another session's live lock → read-only, no re-arm, no marker writes.
- **Wake delivery** — `pi.sendUserMessage` with the operational-input wire encoding (below), as a `followUp`, telling the model to run `bin/fm-wake-drain.sh`.
- **Model-facing surface** — registers the `fm_watch_arm_pi` tool (plus `/fm-watch-arm-pi` command) whose description/promptGuidelines aggressively scope it: *call only for the first cycle or explicit repair; ordinary re-arming is automatic; never run the arm script through bash*. Redundant calls return "unchanged" no-ops. This keeps the model from burning tokens/turns on supervision the extension already owns.

### 3. `fm-calm.ts` (277 lines) + `lib/` — `/calm` presentation toggle

A conversation-only transcript view (genuine user prompts + genuine assistant text + Pi's working indicator; everything else hidden) that **never touches model context, delivery, session storage, or export content** — presentation only:

- **Built-in tool re-registration** — imports Pi's factory functions (`createReadToolDefinition`, `createBashToolDefinition`, … all 7 built-ins) and re-registers each with `renderShell: "self"`, wrapped `renderCall`/`renderResult` that return an empty `Container` when calm hides that class, and a per-cwd definition cache so `execute` still delegates to the correct-cwd original.
- **Export fidelity** — an `onTerminalInput` hook watches for `/export` and `/share` submissions, temporarily flips to stock rendering, then double-toggles `ctx.ui.setToolsExpanded()` to force a redraw. Exports always contain the full transcript.
- **Persistence** — the toggle is stored at `$FM_HOME/config/calm` via atomic write (temp file with `wx` + `rename`, mode 0600), reloaded every `session_start`.
- **`lib/fm-calm-visibility.ts`** — a 20-class transcript taxonomy (`genuine-user-prompt`, `assistant-thinking`, `tool-result`, `synthetic-user`, …) with exactly three visible in calm. Cross-extension state is shared by broadcasting on `pi.events` (the watch extension subscribes so its custom tool renders respect calm) — extensions communicate via the event bus, not shared module state.
- **`lib/fm-calm-assistant-layout.ts` / `fm-calm-operational-user-layout.ts`** — the escape hatch where Pi exposes **no supported renderer**: prototype patches on `AssistantMessageComponent.updateContent` (filters `thinking` blocks from the presentation copy only) and `InteractiveMode.addMessageToChat` (substitutes a `UserMessageComponent` subclass whose `render()` returns `[]` for hidden operational input). Both are explicitly pinned — `Symbol.for("firstmate:calm-assistant-layout:pi-0.81.1")` — installed idempotently with hot-reinstall of the predicate closures, and throw loudly if the patched method vanishes in a Pi upgrade.
- **`lib/fm-operational-input.ts`** — a thin wrapper that shells out to `bin/fm-operational-input.sh` for encode/classify. The bash script is the **single cross-language owner** of the wire protocol:
  `U+2063 FIRSTMATE_OP: v1 <kind>: <body>` — an invisible-separator prefix + versioned kind header (`session-start | watcher | turn-end-guard | away-supervisor | from-firstmate | launch-brief`) so injected prompts are structurally typed and can never be mistaken for captain-authored input.

## Testing & evidence discipline

- `tests/fm-pi-primary-types.test.sh` — runs `tsc --strict --noEmit` for the tracked extensions **against the installed Pi's actual type declarations**, so a Pi upgrade that breaks the assumed API surface fails CI-style rather than at runtime.
- `tests/fm-pi-watch-extension.test.sh` — simulates actionable and empty child closes against the real close handlers, *blocks prompt delivery to prove the successor launches first*, verifies single-flight, swaps the session lock mid-close to prove ownership is rechecked, and hangs successors to prove bounded fallback delivery.
- `tests/fm-pi-primary-live-e2e.test.sh` (env-gated) — real Pi TUI, real watcher, real model, pinned provider/model.
- The docs (`docs/watcher-continuity.md`, `docs/turnend-guard.md`, `docs/calm-mode-feasibility.md`, `docs/sessionstart-nudge.md`) are **contracts with dated reproduction evidence**: exact harness versions, exact commands, observed outputs, and explicit statements of which document owns which decision.

## Pi ExtensionAPI surface this maps out (verified-in-anger)

| Capability | API |
|---|---|
| Lifecycle events | `pi.on("session_start")` (with `reason: startup\|new\|resume\|…`), `agent_settled`, `session_shutdown` |
| Blocking tool interception | `pi.on("tool_call")` → return `{block: true, reason}` |
| Inject a user-role turn | `pi.sendUserMessage(content, {deliverAs: "followUp"})` |
| Inject hidden context | `pi.sendMessage({customType, content, display: false, details})` |
| Custom tools | `pi.registerTool({name, description, promptSnippet, promptGuidelines, parameters (typebox), renderShell/renderCall/renderResult, execute})` |
| Slash commands | `pi.registerCommand(name, {description, handler(args, ctx)})` |
| Custom entry rendering | `pi.registerEntryRenderer<T>(type, fn)` |
| Cross-extension bus | `pi.events.emit/on` |
| TUI control | `ctx.ui.setToolsExpanded/getToolsExpanded, setWorkingVisible, setHiddenThinkingLabel, onTerminalInput, getEditorText, setStatus, notify` |
| Built-in re-skin | import `create<Tool>ToolDefinition(cwd)` factories, re-register with wrappers |

## Takeaways for the PRP / kild lane

1. **Same architecture shape as ours, inverted ownership.** firstmate solves multi-harness portability with *shared bash predicates + thin per-harness lifecycle adapters* (five adapters, one contract each in `docs/`). Our `sync_plugin.py` renders per-harness *prompt packs*; firstmate renders per-harness *hook code*. The two compose — a kild lane driving Pi could load exactly this kind of extension.
2. **Turn-end guard is the missing primitive for autonomous loops.** `prp_loop.py` currently trusts the harness to keep going; firstmate's `agent_settled` + shared predicate + forced follow-up (with a recursion latch, failing open) is a proven pattern for "the agent must not stop while work is in flight," including on harnesses without blocking Stop hooks. Their motivating incident: a parked gate sat unwatched for ~9 hours.
3. **Typed operational-input protocol.** The `U+2063 FIRSTMATE_OP: v1 <kind>:` wire form solves a problem we'll hit in kild: injected/synthetic prompts must be structurally distinguishable from genuine user input, versioned, and owned by exactly one implementation (bash CLI; TS shells out to it).
4. **Zero-token supervision.** Watcher sleeps in a child process; the model is woken only with an actionable reason, and the *successor watcher is armed before the wake is delivered*. Contrast with polling-style loops that burn turns checking state.
5. **Exact-version prototype patching, done responsibly.** Where the host lacks a supported surface, they patch — but pin the patch to a version in the symbol name and in comments, throw loudly on mismatch, and run strict typecheck against the installed host's types in tests. A defensible template for any harness monkey-patching we're ever tempted to do.
6. **Extension-version markers.** Writing `sha256(file) + pid` to a state marker lets session-start tooling detect a stale loaded extension after an update — cheap and effective.

Clone studied at: `<scratchpad>/firstmate` (session-local; re-clone to revisit).
