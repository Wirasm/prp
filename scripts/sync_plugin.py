#!/usr/bin/env python3
"""Generate the distribution targets from the source of truth in .claude/.

Targets:

1. plugins/prp-core/ — the Claude Code plugin.
   - skills/  <- skills under .claude/skills/, minus PLUGIN_EXCLUDED_SKILLS
     (personal experiments that must not reach anyone else's install),
     verbatim except SKILL.md launcher paths in
     LAUNCHER_REWRITES (scripts invoked from a .claude/ path locally) are
     rewritten to their ${CLAUDE_PLUGIN_ROOT} form
   - agents/  <- .claude/agents/, minus EXCLUDED_AGENTS
   Everything else under plugins/prp-core/ (.claude-plugin/, hooks/, README.md)
   is plugin-only and never touched.

2. .agents/skills/ — the render Codex consumes. NOTE the discovery path: Codex
   reads $CODEX_HOME/skills (~/.codex/skills when CODEX_HOME is unset). It does
   NOT read ~/.agents/skills — in Codex, .agents/ is the *plugin* location
   (~/.agents/plugins/marketplace.json). Verified against codex-cli 0.147.0.
   For user-level use, symlink each rendered skill into the discovery dir; a
   symlink tracks every sync, a copy silently goes stale:
       for d in <repo>/.agents/skills/prp-*; do
         ln -s "$d" ~/.codex/skills/"$(basename "$d")"
       done
   Per-skill rather than linking the whole directory, because ~/.codex/skills
   is shared with every other Codex skill the user installs. That sharing cuts
   both ways: the stale prune below deletes anything in .agents/skills that
   .claude/skills did not generate, so nothing foreign should be parked there.
   Skills from .claude/skills/ minus CODEX_EXCLUDED_SKILLS. Personal
   experiments render here on purpose: this target is the author's own Codex
   install, not a public distribution. With Claude-isms
   rewritten (CODEX_REWRITES): Task-tool subagent dispatch -> explicit
   "spawn the X subagent" delegation, prp-core: namespace dropped (Codex agent
   names are flat), /prp-x -> $prp-x mentions, launcher paths, an Arguments
   note replacing Claude's $ARGUMENTS substitution, argument-hint stripped.

3. .codex/agents/*.toml — the pack's subagents as Codex custom agents,
   converted from .claude/agents/*.md (frontmatter name/description; body ->
   developer_instructions), minus EXCLUDED_AGENTS. Symlink for user-level use
   the same way: ln -s <repo>/.codex/agents ~/.codex/agents

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

# Manual experiments remain top-level so Claude Code can discover explicit
# invocations. They are kept out of the plugin other people install, but still
# render to .agents/skills so the author can exercise them in Codex.
PLUGIN_EXCLUDED_SKILLS = {"prp-deliver"}

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

EXCLUDED_AGENTS = {"gpui-researcher.md"}  # personal, not part of the pack

# Claude-harness-specific skills that have no meaningful Codex render (yet):
# prp-orchestrate and prp-meta-skill ARE rendered — orchestrate's delegation
# mechanics rewrite to harness-agnostic delegation language,
# and meta-skill's authored-skill paths map to the local
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
# Which per-skill rewrites actually matched something this run. A rewrite that
# never fires is obsolete or mistyped, and until it is reported it fails silently:
# the Claude-ism it was written to remove simply survives into the Codex render.
# That is how `run_in_background` and an `isolation: "worktree"` spawn parameter —
# neither of which exists on Codex — reached the rendered orchestrate skill.
FIRED_REWRITES: set[tuple[str, str]] = set()

CODEX_SKILL_REWRITES: dict[str, list[tuple[re.Pattern, str]]] = {
    "prp-loop": [
        (re.compile(r'prp_loop\.py "\$ARGUMENTS"'), 'prp_loop.py "$ARGUMENTS" --cli codex'),
        (re.compile(r"prp_loop\.py --resume"), "prp_loop.py --resume --cli codex"),
    ],
    # Both harnesses now pre-create the checkout with prp-worktree, so only the
    # Claude-only spawn mechanics need removing: a warning about an `isolation`
    # parameter Codex does not have, and `run_in_background`.
    "prp-orchestrate": [
        (re.compile(r"Do not use the Agent tool's `isolation: \"worktree\"` for a workstream that may be "
                    r"resumed\. The harness\s+reclaims that checkout once it releases an unchanged owner, "
                    r"which is what a finished delivery looks\s+like, and the next resume lands silently in "
                    r"the operator's own checkout\.\n\n"),
         ""),
        (re.compile(r"one agent, `run_in_background` \(the default\), in its own managed worktree\."),
         "one background agent in its own managed worktree."),
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
        if pattern.search(text):
            FIRED_REWRITES.add((skill, pattern.pattern))
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


def _all_skill_files() -> list[Path]:
    return _walk(SRC_SKILLS)


def expected_files() -> dict[Path, bytes]:
    """Map of repo-relative path -> expected content, across all targets."""
    expected: dict[Path, bytes] = {}

    for src in _all_skill_files():
        if src.suffix != ".md":
            continue
        text = src.read_text()
        if "# --- PRP store resolver" in text and PRP_RESOLVER_BLOCK not in text:
            sys.exit(f"{src}: PRP store resolver differs from the canonical block")

    # 1. Claude Code plugin
    for src in _all_skill_files():
        rel = src.relative_to(SRC_SKILLS)
        skill = rel.parts[0]
        if skill in PLUGIN_EXCLUDED_SKILLS:
            continue
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
    for src in _all_skill_files():
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

    return expected


def actual_files() -> dict[Path, bytes]:
    actual: dict[Path, bytes] = {}
    for base_rel in (PLUGIN_SKILLS, PLUGIN_AGENTS, CODEX_SKILLS, CODEX_AGENTS):
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

    dead = [
        (skill, pat.pattern)
        for skill, rules in CODEX_SKILL_REWRITES.items()
        for pat, _ in rules
        if (skill, pat.pattern) not in FIRED_REWRITES
    ]
    for skill, pattern in dead:
        print(f"dead rewrite ({skill}): {pattern[:90]}")
    if dead:
        print(
            f"{len(dead)} Codex rewrite(s) matched nothing — the source moved under them, so "
            "whatever each was written to remove is now in the render verbatim. Fix or delete."
        )

    if args.check:
        for rel in missing:
            print(f"missing: {rel}")
        for rel in stale:
            print(f"stale (not in source): {rel}")
        for rel in changed:
            print(f"differs: {rel}")
        if missing or stale or changed or dead:
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
