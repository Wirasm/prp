#!/usr/bin/env python3
"""Generate the distribution targets from the source of truth in .claude/.

Targets:

1. plugins/prp-core/ — the Claude Code plugin.
   - skills/  <- .claude/skills/, verbatim except SKILL.md launcher paths in
     LAUNCHER_REWRITES (scripts invoked from a .claude/ path locally) are
     rewritten to their ${CLAUDE_PLUGIN_ROOT} form
   - agents/  <- .claude/agents/, minus EXCLUDED_AGENTS
   Everything else under plugins/prp-core/ (.claude-plugin/, hooks/, README.md)
   is plugin-only and never touched.

2. .agents/skills/ — the OpenAI Codex CLI render. Codex auto-discovers a repo's
   .agents/skills; for user-level use, SYMLINK rather than copy:
       ln -s <repo>/.agents/skills ~/.agents/skills
   A symlink stays current on every sync; a copy silently goes stale. Two
   consequences of the symlink, both load-bearing: ~/.agents/skills IS this
   repo's directory, so a globally-installed Codex skill lands inside the git
   repo (see the .gitignore rule), and the stale prune below deletes anything
   here not generated from .claude/skills. Keep ~/.agents/skills exclusively
   prp's — route other skills through ~/.codex/skills instead.
   Skills from .claude/skills/ minus CODEX_EXCLUDED_SKILLS, with Claude-isms
   rewritten (CODEX_REWRITES): Task-tool subagent dispatch -> explicit
   "spawn the X subagent" delegation, prp-core: namespace dropped (Codex agent
   names are flat), /prp-x -> $prp-x mentions, launcher paths, an Arguments
   note replacing Claude's $ARGUMENTS substitution, argument-hint stripped.

3. .codex/agents/*.toml — the pack's subagents as Codex custom agents,
   converted from .claude/agents/*.md (frontmatter name/description; body ->
   developer_instructions), minus EXCLUDED_AGENTS. Symlink for user-level use
   the same way: ln -s <repo>/.codex/agents ~/.codex/agents

4. profiles/kild/skills/ — the kild-lane profile (primitives-audit slice 7):
   only KILD_INCLUDED_SKILLS, each with a lane preamble that overrides
   driver-owning steps (branches, worktrees, push/PR, artifact archival) and
   pi-lane rewrites (inline analysis instead of Task-tool subagents, bare
   agent names, no slash mentions). Deliberately outside .agents/ so it is
   never discovered — the kild engine assigns it to sessions explicitly.

The prp-research-team Stop hook is deliberately NOT ported: prp-research-team
is Claude-only (agent teams), so the hook has nothing to validate in Codex.

Usage:
    python3 scripts/sync_plugin.py          # regenerate all targets
    python3 scripts/sync_plugin.py --check  # verify; exit 1 if out of sync
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_SKILLS = ROOT / ".claude" / "skills"
SRC_AGENTS = ROOT / ".claude" / "agents"

PRP_RESOLVER_BLOCK = """# --- PRP store resolver (canonical; keep byte-identical across skills) ---
_gd="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"
case "$_gd" in */.git) _root="${_gd%/.git}" ;; "") _root="$PWD" ;; *) _root="$_gd" ;; esac
_root="$(cd "$_root" && pwd -P)"
_name="$(basename "$_root" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/^-*//;s/-*$//')"
PRP_DIR="${PRP_HOME:-$HOME/.prp}/${_name:-project}-$(printf %s "$_root" | git hash-object --stdin | cut -c1-8)"
mkdir -p "$PRP_DIR"; [ -f "$PRP_DIR/project.json" ] || printf '{"path": "%s", "name": "%s"}\\n' "$_root" "${_name:-project}" > "$PRP_DIR/project.json"
"""

# Generated roots (repo-relative). Everything under these paths is owned by
# this script; stale files are deleted on regeneration.
PLUGIN_SKILLS = Path("plugins/prp-core/skills")
PLUGIN_AGENTS = Path("plugins/prp-core/agents")
CODEX_SKILLS = Path(".agents/skills")
CODEX_AGENTS = Path(".codex/agents")
# Deliberately NOT under .agents/ — the kild profile must never be discovered;
# the kild engine hands it to sessions explicitly (ResourceLoader).
KILD_SKILLS = Path("profiles/kild/skills")

EXCLUDED_AGENTS = {"gpui-researcher.md"}  # personal, not part of the pack

# Claude-harness-specific skills that have no meaningful Codex render (yet):
# prp-orchestrate and prp-meta-skill ARE rendered — orchestrate's delegation
# mechanics rewrite to harness-agnostic language (kild rooms / subagents /
# headless fallback), and meta-skill's authored-skill paths map to the local
# discovery dir (.agents/skills).
CODEX_EXCLUDED_SKILLS = {
    "prp-research-team",  # targets Claude Code's experimental agent-teams feature
}

# SKILL.md files whose bodies invoke a bundled script by its repo-local path;
# each target rewrites the launcher to its own location.
LAUNCHER_REWRITES: dict[str, tuple[str, str, str]] = {
    # skill dir -> (local path, plugin path, codex path)
    "prp-loop": (
        ".claude/skills/prp-loop/scripts/prp_loop.py",
        "${CLAUDE_PLUGIN_ROOT}/skills/prp-loop/scripts/prp_loop.py",
        ".agents/skills/prp-loop/scripts/prp_loop.py",
    ),
    "prp-worktree": (
        ".claude/skills/prp-worktree/scripts/worktree.py",
        "${CLAUDE_PLUGIN_ROOT}/skills/prp-worktree/scripts/worktree.py",
        ".agents/skills/prp-worktree/scripts/worktree.py",
    ),
}

SKIP_DIRS = {"__pycache__"}
SKIP_SUFFIXES = {".pyc", ".pyo"}

# ---------- Codex text transforms ----------

ARGS_NOTE = (
    "> **Arguments:** `$ARGUMENTS` (and `$1`, `$2`, ...) refer to the arguments given "
    "when this skill was invoked. Take them from the user's request; if absent, infer "
    "them from the conversation.\n"
)


def _spawn(m: re.Match) -> str:
    verb = "Spawn" if m.group(1) == "U" else "spawn"
    return f"{verb} the `{m.group(2)}` subagent"


# Applied in order to every rendered Codex markdown file.
CODEX_REWRITES: list[tuple[re.Pattern, object]] = [
    # Task-tool subagent dispatch -> Codex explicit delegation
    (re.compile(r'([Uu])se Task tool with `subagent_type="prp-core:([a-z-]+)"`'), _spawn),
    (re.compile(r'\(subagent_type="prp-core:([a-z-]+)"\)'), r"(spawn as the `\1` subagent)"),
    (re.compile(r"using multiple Task tool calls in a single message"),
     "by spawning them as subagents in one step"),
    (re.compile(r"in a \*\*single message with multiple Task tool calls\*\*"),
     "as **parallel subagents spawned in one step**"),
    (re.compile(r"in a \*\*single message with two Task tool calls\*\*"),
     "as **two parallel subagents spawned in one step**"),
    (re.compile(r"When launching each agent via Task tool:"), "When spawning each subagent:"),
    (re.compile(r"using Task tool subagents"), "using parallel subagents"),
    # Skill-tool dispatch -> Codex skill invocation (must precede the prp-core: strip)
    (re.compile(r'Skill tool, `skill: "prp-core:([a-z-]+)"`, `args: "([^"]*)"`\.'),
     r"Run the `\1` skill with arguments `\2`."),
    # Codex custom-agent names are flat — drop the plugin namespace
    (re.compile(r"prp-core:"), ""),
    # Claude @-mention context include -> Codex AGENTS.md reality
    (re.compile(r"CLAUDE\.md rules: @CLAUDE\.md"),
     "Project rules: follow the loaded AGENTS.md context; also read CLAUDE.md if the project has one."),
    # prose references to the Claude headless CLI
    (re.compile(r"`claude -p`"), "`codex exec`"),
    # slash invocation -> Codex $skill mention (lookbehind protects file paths)
    (re.compile(r"(?<![\w/])/prp-"), "$prp-"),
    # bundled-script launcher paths
    (re.compile(r"\.claude/skills/prp-worktree/scripts/worktree\.py"),
     ".agents/skills/prp-worktree/scripts/worktree.py"),
    # any remaining skill-tree path: the local harness discovers .agents/skills
    (re.compile(r"\.claude/skills/"), ".agents/skills/"),
    # Claude Agent-tool spawn phrasing -> harness-neutral
    (re.compile(r"the Agent/Task tool"), "your delegation tool"),
]

# Per-skill extras, applied after the global list.
CODEX_SKILL_REWRITES: dict[str, list[tuple[re.Pattern, str]]] = {
    "prp-loop": [
        (re.compile(r'prp_loop\.py "\$ARGUMENTS"'), 'prp_loop.py "$ARGUMENTS" --cli codex'),
        (re.compile(r"prp_loop\.py --resume"), "prp_loop.py --resume --cli codex"),
    ],
    # Orchestrate is written against Claude Code's native agent tools; render the
    # mechanics harness-agnostic (kild rooms / subagents / headless fallback) while
    # keeping the discipline (decompose, gate, verify, merge) verbatim.
    "prp-orchestrate": [
        (re.compile(r"launch and steer agents with the native agent tools"),
         "launch and steer background agents with your harness's delegation tools"),
        (re.compile(
            r"\*\*Drive everything through the native agent tools\*\* — spawn with "
            r"your delegation tool \(background, worktree isolation\), steer and continue "
            r"with SendMessage, stop with the task-stop tool, check with the "
            r"task-list/status tools\."),
         "**Drive everything through your harness's delegation tools** — spawn background "
         "workstream agents in isolated worktrees (kild rooms via the kild_* tools, or "
         "your subagent mechanism), steer a running agent by sending it a follow-up "
         "message, stop it and check status with the matching controls."),
        (re.compile(r"via SendMessage with the answer"), "via a follow-up message with the answer"),
        (re.compile(r"SendMessage the decision back to the same agent"),
         "message the decision back to the same agent"),
        (re.compile(r"\*\*SendMessage the decision to the same agent\*\*"),
         "**message the decision to the same agent**"),
        (re.compile(r"→ SendMessage to that agent"), "→ send a message to that agent"),
        (re.compile(r"then SendMessage the same agent to proceed"),
         "then message the same agent to proceed"),
        (re.compile(r"and SendMessage them to running agents"), "and send them to running agents"),
        (re.compile(r"either SendMessage a nudge"), "either send a nudge"),
        (re.compile(r"convey it — SendMessage to the affected agent\(s\)"),
         "convey it — message the affected agent(s)"),
        (re.compile(r"prefer SendMessage to the owning agent"), "prefer messaging the owning agent"),
        (re.compile(r"SendMessage continues an agent \*\*with its context intact\*\* — always prefer it"),
         "A follow-up message continues an agent **with its context intact** — always prefer that"),
        (re.compile(r"the handle for SendMessage, stop, and status"),
         "the handle for messaging, stopping, and status checks"),
        (re.compile(r"\*\*Steer / continue\*\*: SendMessage to the agent ID"),
         "**Steer / continue**: send a message to the agent ID"),
        (re.compile(r"no SendMessage \(course-correct"), "no live steering (course-correct"),
        (re.compile(r"agent-tool call shapes, the workstream prompt template, SendMessage/stop/status patterns"),
         "launch call shapes, the workstream prompt template, steering/stop/status patterns"),
        (re.compile(r"one agent, `run_in_background` \(the default\), \*\*`isolation: \"worktree\"`\*\*"),
         "one background agent with **worktree isolation**"),
        (re.compile(r"\*\*Stop\*\*: the task-stop tool against the workstream's task\."),
         "**Stop**: your harness's stop control against the workstream's agent."),
        (re.compile(r"\*\*Status\*\*: the task-list/status tools give live agent state"),
         "**Status**: the agent list/status controls give live agent state"),
        (re.compile(r"wire project hooks on the relevant events \(e\.g\. SubagentStop\) in `\.claude/settings\.json`"),
         "wire hooks on the relevant agent-stop events if your harness supports them"),
        (re.compile(r" — consult the current Claude Code hooks docs for event names and payloads\."), "."),
        (re.compile(r'nohup claude -p "<workstream prompt>" \\\n  --dangerously-skip-permissions --output-format stream-json --verbose \\\n'),
         'nohup codex exec --dangerously-bypass-approvals-and-sandbox "<workstream prompt>" \\\n'),
        (re.compile(r"Agent-tool worktrees are auto-removed when unchanged"),
         "Harness-managed worktrees may be auto-removed when unchanged"),
        (re.compile(r"An agent-tool worktree holds"), "An agent worktree holds"),
    ],
    # Meta-skill: only its meta-documentation of Claude-only mechanics needs a touch;
    # authored-skill paths are handled by the global .claude/skills -> .agents/skills map.
    "prp-meta-skill": [
        (re.compile(r"Claude-only mechanics \(subagent fan-out, Stop-hook loops, `\$\{CLAUDE_PLUGIN_ROOT\}`\)"),
         "Claude-only mechanics (subagent fan-out, Stop-hook loops, plugin-root path variables)"),
    ],
}

# Nothing Claude-specific may survive in the Codex render.
CODEX_FORBIDDEN = (
    "subagent_type", "Task tool", "Skill tool", "prp-core:", "argument-hint:",
    "@CLAUDE.md", "${CLAUDE_PLUGIN_ROOT}", ".claude/skills/",
    "SendMessage",
)

# ---------- kild-lane profile (audit slice 7) ----------
# The kild engine assigns this skill set to room sessions via an explicit
# ResourceLoader — the driver grants capabilities; nothing here is discovered.
# Driver-owning skills (worktrees, branches, push/PR, orchestration loops) are
# structurally absent; the included skills get a lane preamble that overrides
# their driver-owning steps until true process-primitive variants exist.

KILD_INCLUDED_SKILLS = {
    "prp-commit",             # rooms end committed — commit is in-lane
    "prp-debug",
    "prp-codebase-question",
    "prp-prd",
    "prp-plan",               # writes plan artifacts only
    "prp-implement",          # lane note strips branch/push/archive behavior
    "prp-review",             # lane note forbids gh pr checkout
}

KILD_LANE_NOTE = (
    "> **Kild lane:** you are running inside a kild room, in a workspace "
    "(worktree + branch) the kild engine assigned. The driver owns isolation and "
    "publishing — SKIP any step below that creates or switches branches or "
    "worktrees, pulls or rebases the base branch, pushes, opens PRs, or "
    "moves/archives plan artifacts, and never run `gh pr checkout`. Your job ends "
    "at implement → validate → commit in the current workspace, reporting "
    "evidence. Where a step spawns subagents, do that analysis inline — or ask "
    "the room's orchestrator to invite a helper agent.\n"
)


def _inline(m: re.Match) -> str:
    verb = "Do" if m.group(1) == "U" else "do"
    return f"{verb} the `{m.group(2)}` analysis below inline (kild lane: no subagents)"


# Applied in order to every rendered kild-profile markdown file.
KILD_REWRITES: list[tuple[re.Pattern, object]] = [
    # Task-tool subagent dispatch -> inline execution in the room worker
    (re.compile(r'([Uu])se Task tool with `subagent_type="prp-core:([a-z-]+)"`'), _inline),
    (re.compile(r'\(subagent_type="prp-core:([a-z-]+)"\)'), r"(the `\1` analysis, done inline)"),
    (re.compile(r"[Ll]aunch (two|three|the) specialized agents in parallel using multiple Task tool calls in a single message"),
     r"Work through the \1 specialized analyses inline, one after another"),
    (re.compile(r"using multiple Task tool calls in a single message"),
     "by working through them inline, one after another"),
    (re.compile(r"in a \*\*single message with multiple Task tool calls\*\*"),
     "**inline, one after another**"),
    (re.compile(r"in a \*\*single message with two Task tool calls\*\*"),
     "**inline, one after the other**"),
    (re.compile(r"When launching each agent via Task tool:"), "For each analysis, inline:"),
    (re.compile(r"using Task tool subagents"), "inline"),
    # Skill-tool dispatch -> named skill (must precede the prp-core: strip)
    (re.compile(r'Skill tool, `skill: "prp-core:([a-z-]+)"`, `args: "([^"]*)"`\.'),
     r"Use the `\1` skill with arguments `\2`."),
    # pi/kild agent names are bare
    (re.compile(r"prp-core:"), ""),
    # pi loads AGENTS.md and CLAUDE.md natively as context files
    (re.compile(r"CLAUDE\.md rules: @CLAUDE\.md"),
     "Project rules: your loaded context files (AGENTS.md / CLAUDE.md) apply."),
    # pi has no slash-skill mention in prose; name the skill instead
    (re.compile(r"run: `/prp-([a-z-]+)( [^`]*)?`"), r"use the prp-\1 skill\2"),
    (re.compile(r"(?<![\w/])/prp-([a-z-]+)"), r"the prp-\1 skill"),
]

KILD_FORBIDDEN = CODEX_FORBIDDEN


def kild_render_md(text: str, skill: str, src: Path) -> str:
    text = re.sub(r"^argument-hint:[^\n]*\n", "", text, flags=re.M)
    for pattern, repl in KILD_REWRITES:
        text = pattern.sub(repl, text)
    notes = KILD_LANE_NOTE
    if re.search(r"\$ARGUMENTS|\$\d", text):
        notes += "\n" + ARGS_NOTE
    text = _inject_after_frontmatter(text, notes)
    for token in KILD_FORBIDDEN:
        if token in text:
            sys.exit(f"kild render of {src}: forbidden Claude-ism '{token}' survived the rewrite")
    return text


def _inject_after_frontmatter(text: str, note: str) -> str:
    if text.startswith("---"):
        end = text.index("\n---\n", 3) + len("\n---\n")
        return text[:end] + "\n" + note + text[end:]
    first_nl = text.index("\n") + 1
    return text[:first_nl] + "\n" + note + text[first_nl:]


def codex_render_md(text: str, skill: str, src: Path) -> str:
    # strip argument-hint from frontmatter (Codex ignores it; keep the render clean)
    text = re.sub(r"^argument-hint:[^\n]*\n", "", text, flags=re.M)
    for pattern, repl in CODEX_REWRITES:
        text = pattern.sub(repl, text)
    for pattern, repl in CODEX_SKILL_REWRITES.get(skill, []):
        text = pattern.sub(repl, text)
    # Claude substitutes $ARGUMENTS at invocation; Codex has no templating, so
    # tell the model what the placeholder means.
    if re.search(r"\$ARGUMENTS|\$\d", text):
        text = _inject_after_frontmatter(text, ARGS_NOTE)
    for token in CODEX_FORBIDDEN:
        if token in text:
            sys.exit(f"codex render of {src}: forbidden Claude-ism '{token}' survived the rewrite")
    return text


def agent_md_to_toml(src: Path) -> bytes:
    """Convert a Claude agent (.md, YAML frontmatter + prompt body) to a Codex
    custom-agent TOML (name / description / developer_instructions)."""
    text = src.read_text()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        sys.exit(f"{src}: missing frontmatter")
    fm, body = m.group(1), m.group(2).strip() + "\n"
    fields = {}
    for line in fm.splitlines():
        mm = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if mm:
            fields[mm.group(1)] = mm.group(2).strip()
    name, desc = fields.get("name", ""), fields.get("description", "")
    if not name or not desc:
        sys.exit(f"{src}: frontmatter must define name and description")
    desc = re.sub(r"prp-core:", "", desc)
    body = re.sub(r"prp-core:", "", body)
    for value, label in ((desc, "description"), (body, "body")):
        if "'''" in value:
            sys.exit(f"{src}: {label} contains ''' — not representable as a TOML literal string")
    return (
        f'name = "{name}"\n'
        f"description = '''{desc}'''\n"
        f"developer_instructions = '''\n{body}'''\n"
    ).encode()


# ---------- expected trees ----------

def _walk(base: Path) -> list[Path]:
    return sorted(
        p for p in base.rglob("*")
        if p.is_file()
        and not SKIP_DIRS.intersection(p.relative_to(base).parts)
        and p.suffix not in SKIP_SUFFIXES
    )


def expected_files() -> dict[Path, bytes]:
    """Map of repo-relative path -> expected content, across all targets."""
    expected: dict[Path, bytes] = {}

    for src in _walk(SRC_SKILLS):
        if src.suffix != ".md":
            continue
        text = src.read_text()
        if "# --- PRP store resolver" in text and PRP_RESOLVER_BLOCK not in text:
            sys.exit(f"{src}: PRP store resolver differs from the canonical block")

    # 1. Claude Code plugin
    for src in _walk(SRC_SKILLS):
        rel = src.relative_to(SRC_SKILLS)
        skill = rel.parts[0]
        content = src.read_bytes()
        if skill in LAUNCHER_REWRITES and rel == Path(skill) / "SKILL.md":
            local, plugin, _ = LAUNCHER_REWRITES[skill]
            text = content.decode()
            if local not in text:
                sys.exit(f"{src}: expected launcher path '{local}' not found")
            content = text.replace(local, plugin).encode()
        expected[PLUGIN_SKILLS / rel] = content
    for src in _walk(SRC_AGENTS):
        if src.name in EXCLUDED_AGENTS:
            continue
        expected[PLUGIN_AGENTS / src.relative_to(SRC_AGENTS)] = src.read_bytes()

    # 2. Codex skills render
    for src in _walk(SRC_SKILLS):
        rel = src.relative_to(SRC_SKILLS)
        skill = rel.parts[0]
        if skill in CODEX_EXCLUDED_SKILLS:
            continue
        if src.suffix == ".md":
            text = src.read_text()
            if skill in LAUNCHER_REWRITES and rel == Path(skill) / "SKILL.md":
                local, _, codex = LAUNCHER_REWRITES[skill]
                if local not in text:
                    sys.exit(f"{src}: expected launcher path '{local}' not found")
                text = text.replace(local, codex)
            expected[CODEX_SKILLS / rel] = codex_render_md(text, skill, src).encode()
        else:
            expected[CODEX_SKILLS / rel] = src.read_bytes()

    # 3. Codex custom agents (TOML)
    for src in _walk(SRC_AGENTS):
        if src.name in EXCLUDED_AGENTS:
            continue
        expected[CODEX_AGENTS / (src.stem + ".toml")] = agent_md_to_toml(src)

    # 4. kild-lane profile (handed to sessions by the kild engine, never discovered)
    for src in _walk(SRC_SKILLS):
        rel = src.relative_to(SRC_SKILLS)
        skill = rel.parts[0]
        if skill not in KILD_INCLUDED_SKILLS:
            continue
        if src.suffix == ".md":
            expected[KILD_SKILLS / rel] = kild_render_md(src.read_text(), skill, src).encode()
        else:
            expected[KILD_SKILLS / rel] = src.read_bytes()

    return expected


def actual_files() -> dict[Path, bytes]:
    actual: dict[Path, bytes] = {}
    for base_rel in (PLUGIN_SKILLS, PLUGIN_AGENTS, CODEX_SKILLS, CODEX_AGENTS, KILD_SKILLS):
        base = ROOT / base_rel
        if base.exists():
            for p in _walk(base):
                actual[base_rel / p.relative_to(base)] = p.read_bytes()
    return actual


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="verify only; exit 1 if out of sync")
    args = ap.parse_args()

    expected = expected_files()

    # sanity: generated TOML must parse
    try:
        import tomllib
        for rel, content in expected.items():
            if rel.suffix == ".toml":
                tomllib.loads(content.decode())
    except ModuleNotFoundError:
        pass  # tomllib is 3.11+; the check is best-effort

    actual = actual_files()
    stale = sorted(set(actual) - set(expected))
    missing = sorted(set(expected) - set(actual))
    changed = sorted(r for r in set(expected) & set(actual) if expected[r] != actual[r])

    if args.check:
        for rel in missing:
            print(f"missing: {rel}")
        for rel in stale:
            print(f"stale (not in source): {rel}")
        for rel in changed:
            print(f"differs: {rel}")
        if missing or stale or changed:
            sys.exit("targets are out of sync — run: python3 scripts/sync_plugin.py")
        print("all targets in sync")
        return

    for rel in missing + changed:
        dst = ROOT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(expected[rel])
        print(f"wrote  {rel}")
    for rel in stale:
        (ROOT / rel).unlink()
        print(f"removed {rel}")
    if not (missing or changed or stale):
        print("all targets already in sync — nothing to do")


if __name__ == "__main__":
    main()
