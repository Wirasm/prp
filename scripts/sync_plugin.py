#!/usr/bin/env python3
"""Generate the distribution targets from the source of truth in .claude/.

Targets:

1. plugins/prp-core/ — the Claude Code plugin.
   - skills/  <- .claude/skills/, verbatim except SKILL.md launcher paths in
     LAUNCHER_REWRITES (scripts invoked from a .claude/ path locally) are
     rewritten to their ${CLAUDE_PLUGIN_ROOT} form
   - prp-loop/scripts/prp_loop.py is added, copied from .claude/PRPs/scripts/
   - agents/  <- .claude/agents/, minus EXCLUDED_AGENTS
   Everything else under plugins/prp-core/ (.claude-plugin/, hooks/, README.md)
   is plugin-only and never touched.

2. .agents/skills/ — the OpenAI Codex CLI render (Codex auto-discovers a repo's
   .agents/skills; copy the directory to ~/.agents/skills for user-level use).
   Skills from .claude/skills/ minus CODEX_EXCLUDED_SKILLS, with Claude-isms
   rewritten (CODEX_REWRITES): Task-tool subagent dispatch -> explicit
   "spawn the X subagent" delegation, prp-core: namespace dropped (Codex agent
   names are flat), /prp-x -> $prp-x mentions, launcher paths, an Arguments
   note replacing Claude's $ARGUMENTS substitution, argument-hint stripped.

3. .codex/agents/*.toml — the pack's subagents as Codex custom agents,
   converted from .claude/agents/*.md (frontmatter name/description; body ->
   developer_instructions), minus EXCLUDED_AGENTS.

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
SRC_LOOP_SCRIPT = ROOT / ".claude" / "PRPs" / "scripts" / "prp_loop.py"

# Generated roots (repo-relative). Everything under these paths is owned by
# this script; stale files are deleted on regeneration.
PLUGIN_SKILLS = Path("plugins/prp-core/skills")
PLUGIN_AGENTS = Path("plugins/prp-core/agents")
CODEX_SKILLS = Path(".agents/skills")
CODEX_AGENTS = Path(".codex/agents")

EXCLUDED_AGENTS = {"gpui-researcher.md"}  # personal, not part of the pack

# Claude-harness-specific skills that have no meaningful Codex render (yet):
CODEX_EXCLUDED_SKILLS = {
    "prp-orchestrate",    # drives Claude Code's native agent tools end to end
    "prp-meta-skill",     # authors Claude Code skills (.claude paths, Claude frontmatter)
    "prp-research-team",  # targets Claude Code's experimental agent-teams feature
}

# SKILL.md files whose bodies invoke a bundled script by its repo-local path;
# each target rewrites the launcher to its own location.
LAUNCHER_REWRITES: dict[str, tuple[str, str, str]] = {
    # skill dir -> (local path, plugin path, codex path)
    "prp-loop": (
        ".claude/PRPs/scripts/prp_loop.py",
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
    (re.compile(r"\.claude/PRPs/scripts/prp_loop\.py"),
     ".agents/skills/prp-loop/scripts/prp_loop.py"),
    (re.compile(r"\.claude/skills/prp-worktree/scripts/worktree\.py"),
     ".agents/skills/prp-worktree/scripts/worktree.py"),
]

# Per-skill extras, applied after the global list.
CODEX_SKILL_REWRITES: dict[str, list[tuple[re.Pattern, str]]] = {
    "prp-loop": [
        (re.compile(r'prp_loop\.py "\$ARGUMENTS"'), 'prp_loop.py "$ARGUMENTS" --cli codex'),
        (re.compile(r"prp_loop\.py --resume"), "prp_loop.py --resume --cli codex"),
    ],
}

# Nothing Claude-specific may survive in the Codex render.
CODEX_FORBIDDEN = (
    "subagent_type", "Task tool", "prp-core:", "argument-hint:",
    "@CLAUDE.md", "${CLAUDE_PLUGIN_ROOT}", ".claude/skills/",
)


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
        if text.startswith("---"):
            end = text.index("\n---\n", 3) + len("\n---\n")
            text = text[:end] + "\n" + ARGS_NOTE + text[end:]
        else:
            first_nl = text.index("\n") + 1
            text = text[:first_nl] + "\n" + ARGS_NOTE + text[first_nl:]
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
    expected[PLUGIN_SKILLS / "prp-loop/scripts/prp_loop.py"] = SRC_LOOP_SCRIPT.read_bytes()
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
    expected[CODEX_SKILLS / "prp-loop/scripts/prp_loop.py"] = SRC_LOOP_SCRIPT.read_bytes()

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
