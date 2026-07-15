#!/usr/bin/env python3
"""Generate plugins/prp-core/ from the source of truth in .claude/.

What is generated:
- plugins/prp-core/skills/  <- .claude/skills/, verbatim except:
    * prp-loop/SKILL.md: the launcher path .claude/PRPs/scripts/prp_loop.py is
      rewritten to ${CLAUDE_PLUGIN_ROOT}/skills/prp-loop/scripts/prp_loop.py
    * prp-loop/scripts/prp_loop.py is added, copied from .claude/PRPs/scripts/
- plugins/prp-core/agents/  <- .claude/agents/, minus EXCLUDED_AGENTS
  (personal agents that are not part of the pack)

Everything else under plugins/prp-core/ (.claude-plugin/, hooks/, README.md)
is plugin-only and never touched.

Usage:
    python3 scripts/sync_plugin.py          # regenerate the plugin
    python3 scripts/sync_plugin.py --check  # verify; exit 1 if out of sync
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_SKILLS = ROOT / ".claude" / "skills"
SRC_AGENTS = ROOT / ".claude" / "agents"
SRC_LOOP_SCRIPT = ROOT / ".claude" / "PRPs" / "scripts" / "prp_loop.py"
PLUGIN = ROOT / "plugins" / "prp-core"

EXCLUDED_AGENTS = {"gpui-researcher.md"}

LOOP_PATH_LOCAL = ".claude/PRPs/scripts/prp_loop.py"
LOOP_PATH_PLUGIN = "${CLAUDE_PLUGIN_ROOT}/skills/prp-loop/scripts/prp_loop.py"

SKIP_DIRS = {"__pycache__"}
SKIP_SUFFIXES = {".pyc", ".pyo"}


def _walk(base: Path) -> list[Path]:
    return sorted(
        p for p in base.rglob("*")
        if p.is_file()
        and not SKIP_DIRS.intersection(p.relative_to(base).parts)
        and p.suffix not in SKIP_SUFFIXES
    )


def expected_files() -> dict[Path, bytes]:
    """Map of plugin-relative path -> expected content."""
    expected: dict[Path, bytes] = {}
    for src in _walk(SRC_SKILLS):
        rel = Path("skills") / src.relative_to(SRC_SKILLS)
        content = src.read_bytes()
        if rel == Path("skills/prp-loop/SKILL.md"):
            text = content.decode()
            if LOOP_PATH_LOCAL not in text:
                sys.exit(f"{src}: expected launcher path '{LOOP_PATH_LOCAL}' not found")
            content = text.replace(LOOP_PATH_LOCAL, LOOP_PATH_PLUGIN).encode()
        expected[rel] = content
    expected[Path("skills/prp-loop/scripts/prp_loop.py")] = SRC_LOOP_SCRIPT.read_bytes()
    for src in _walk(SRC_AGENTS):
        if src.name in EXCLUDED_AGENTS:
            continue
        expected[Path("agents") / src.relative_to(SRC_AGENTS)] = src.read_bytes()
    return expected


def actual_files() -> dict[Path, bytes]:
    actual: dict[Path, bytes] = {}
    for area in ("skills", "agents"):
        base = PLUGIN / area
        if base.exists():
            for p in _walk(base):
                actual[Path(area) / p.relative_to(base)] = p.read_bytes()
    return actual


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="verify only; exit 1 if out of sync")
    args = ap.parse_args()

    expected = expected_files()
    actual = actual_files()

    stale = sorted(set(actual) - set(expected))
    missing = sorted(set(expected) - set(actual))
    changed = sorted(r for r in set(expected) & set(actual) if expected[r] != actual[r])

    if args.check:
        for rel in missing:
            print(f"missing: plugins/prp-core/{rel}")
        for rel in stale:
            print(f"stale (not in source): plugins/prp-core/{rel}")
        for rel in changed:
            print(f"differs: plugins/prp-core/{rel}")
        if missing or stale or changed:
            sys.exit("plugin is out of sync — run: python3 scripts/sync_plugin.py")
        print("plugin is in sync")
        return

    for rel in missing + changed:
        dst = PLUGIN / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(expected[rel])
        print(f"wrote  plugins/prp-core/{rel}")
    for rel in stale:
        (PLUGIN / rel).unlink()
        print(f"removed plugins/prp-core/{rel}")
    if not (missing or changed or stale):
        print("plugin already in sync — nothing to do")


if __name__ == "__main__":
    main()
