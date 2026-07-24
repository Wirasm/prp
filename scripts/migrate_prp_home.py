#!/usr/bin/env python3
"""Move one project's legacy PRP artifacts into its per-project home store.

Run from the project to migrate:

    python3 /path/to/prp/scripts/migrate_prp_home.py [--dry-run] [--force]

The script never commits and never edits .gitignore. It refuses linked worktrees by
default because removing tracked legacy paths belongs in the main checkout's index.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ARTIFACT_DIRS = (
    "plans",
    "prds",
    "research",
    "research-plans",
    "reports",
    "reviews",
    "issues",
    "debug",
    "orchestration",
    "features",
)
STATE_FILES = (
    "prp-loop.state.json",
    "prp-loop.run.log",
    "prp-research-team.state",
)
DEAD_GITIGNORE_PATTERNS = (
    ".claude/prp-loop.state.json",
    ".claude/prp-loop.run.log",
    ".claude/PRPs/reviews/*.verdict.json",
    ".claude/prp-research-team.state",
)


class MigrationError(RuntimeError):
    """A condition that makes migration unsafe."""


def git(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def resolve_project(cwd: Path) -> tuple[Path, Path, str, bool]:
    """Return (canonical main root, checkout root, key, is_linked_worktree)."""
    common = git(
        "rev-parse", "--path-format=absolute", "--git-common-dir", cwd=cwd, check=False
    )
    if common.returncode != 0:
        root = cwd.resolve()
        checkout = root
        linked = False
    else:
        common_dir = Path(common.stdout.strip()).resolve()
        root = common_dir.parent if common_dir.name == ".git" else common_dir
        root = root.resolve()

        top = git("rev-parse", "--show-toplevel", cwd=cwd)
        checkout = Path(top.stdout.strip()).resolve()
        git_dir_result = git(
            "rev-parse", "--path-format=absolute", "--git-dir", cwd=cwd
        )
        git_dir = Path(git_dir_result.stdout.strip()).resolve()
        linked = git_dir != common_dir

    name = re.sub(r"[^a-z0-9]+", "-", root.name.lower()).strip("-") or "project"
    hashed = subprocess.run(
        ["git", "hash-object", "--stdin"],
        cwd=cwd,
        input=str(root),
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.strip()
    if not hashed:
        raise MigrationError("git hash-object returned an empty hash")
    return root, checkout, f"{name}-{hashed[:8]}", linked


def validate_registration(store: Path, root: Path, name: str, dry_run: bool) -> None:
    registration = store / "project.json"
    if registration.exists():
        try:
            data = json.loads(registration.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            raise MigrationError(f"cannot read {registration}: {exc}") from exc
        registered_path = data.get("path")
        if registered_path != str(root):
            raise MigrationError(
                f"store collision: {registration} belongs to {registered_path!r}, "
                f"not {str(root)!r}"
            )
        return

    payload = json.dumps({"path": str(root), "name": name}, ensure_ascii=False) + "\n"
    if dry_run:
        print(f"CREATE {registration}: {payload.rstrip()}")
    else:
        store.mkdir(parents=True, exist_ok=True)
        registration.write_text(payload)
        print(f"CREATED {registration}")


def conflict_destination(destination: Path, reserved: set[Path]) -> tuple[Path, bool]:
    if not destination.exists() and destination not in reserved:
        return destination, False
    candidate = destination.with_name(destination.name + ".migrated")
    index = 2
    while candidate.exists() or candidate in reserved:
        candidate = destination.with_name(destination.name + f".migrated.{index}")
        index += 1
    return candidate, True


def files_under(source: Path) -> list[Path]:
    if source.is_symlink() or source.is_file():
        return [source]
    if not source.is_dir():
        return []
    return sorted(
        (path for path in source.rglob("*") if path.is_file() or path.is_symlink()),
        key=lambda path: str(path),
    )


def tracked_paths(checkout: Path, candidates: list[Path]) -> list[str]:
    if not (checkout / ".git").exists():
        probe = git("rev-parse", "--is-inside-work-tree", cwd=checkout, check=False)
        if probe.returncode != 0:
            return []
    relative = [str(path.relative_to(checkout)) for path in candidates]
    if not relative:
        return []
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", *relative],
        cwd=checkout,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return sorted(item.decode() for item in result.stdout.split(b"\0") if item)


def remove_empty_legacy_dirs(legacy_root: Path, dry_run: bool) -> None:
    if dry_run or not legacy_root.exists():
        return
    directories = sorted(
        (path for path in legacy_root.rglob("*") if path.is_dir()),
        key=lambda path: len(path.parts),
        reverse=True,
    )
    for directory in directories:
        try:
            directory.rmdir()
        except OSError:
            pass
    try:
        legacy_root.rmdir()
        print(f"REMOVED empty {legacy_root}")
    except OSError:
        print(f"KEPT non-empty {legacy_root}")


def report_ai_docs(checkout: Path) -> None:
    for path in (checkout / "PRPs" / "ai_docs", checkout / ".claude" / "PRPs" / "ai_docs"):
        if path.is_dir():
            print(f"NOTICE legacy ai_docs left untouched: {path}")


def report_dead_gitignore(checkout: Path) -> None:
    gitignore = checkout / ".gitignore"
    if not gitignore.is_file():
        return
    lines = gitignore.read_text().splitlines()
    matches = [
        (number, line)
        for number, line in enumerate(lines, start=1)
        if line.strip() in DEAD_GITIGNORE_PATTERNS
    ]
    if matches:
        print("Dead .gitignore entries (not edited):")
        for number, line in matches:
            print(f"  {gitignore}:{number}: {line}")


def migrate(args: argparse.Namespace) -> int:
    cwd = Path.cwd()
    root, checkout, key, linked = resolve_project(cwd)
    if linked and not args.force:
        raise MigrationError(
            "refusing to migrate from a linked worktree; run from the main checkout "
            "or pass --force"
        )

    name = re.sub(r"[^a-z0-9]+", "-", root.name.lower()).strip("-") or "project"
    prp_home = Path(os.environ.get("PRP_HOME", str(Path.home() / ".prp"))).expanduser()
    store = prp_home / key

    print(f"Project root: {root}")
    print(f"Checkout:     {checkout}")
    print(f"PRP store:    {store}")
    if args.dry_run:
        print("DRY RUN: no files or Git index entries will be changed")

    validate_registration(store, root, name, args.dry_run)
    report_ai_docs(checkout)

    legacy_root = checkout / ".claude" / "PRPs"
    move_pairs: list[tuple[Path, Path]] = []
    reserved: set[Path] = set()
    conflicts: list[tuple[Path, Path]] = []

    for subdir in ARTIFACT_DIRS:
        source_root = legacy_root / subdir
        for source in files_under(source_root):
            destination = store / subdir / source.relative_to(source_root)
            destination, conflicted = conflict_destination(destination, reserved)
            reserved.add(destination)
            move_pairs.append((source, destination))
            if conflicted:
                conflicts.append((source, destination))

    state_source_root = checkout / ".claude"
    for filename in STATE_FILES:
        source = state_source_root / filename
        if source.is_file() or source.is_symlink():
            destination, conflicted = conflict_destination(store / "state" / filename, reserved)
            reserved.add(destination)
            move_pairs.append((source, destination))
            if conflicted:
                conflicts.append((source, destination))

    tracked = tracked_paths(checkout, [source for source, _ in move_pairs])

    if not move_pairs:
        print("No legacy PRP artifacts or state files found.")
    for source, destination in move_pairs:
        label = "WOULD MOVE" if args.dry_run else "MOVED"
        if not args.dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
        print(f"{label} {source} -> {destination}")

    if conflicts:
        print("Conflicts preserved with migration suffixes:")
        for source, destination in conflicts:
            print(f"  {source} -> {destination}")

    if tracked:
        if args.dry_run:
            print("WOULD RUN git rm --cached for tracked legacy files:")
            for path in tracked:
                print(f"  {path}")
        else:
            subprocess.run(
                ["git", "rm", "-r", "--cached", "-f", "--ignore-unmatch", "--", *tracked],
                cwd=checkout,
                check=True,
            )
            print("Removed migrated tracked files from the Git index.")
        print('Suggested commit: git commit -m "chore(prp): migrate artifacts to PRP home"')

    remove_empty_legacy_dirs(legacy_root, args.dry_run)
    report_dead_gitignore(checkout)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="print actions without changing files")
    parser.add_argument(
        "--force",
        action="store_true",
        help="allow migration from a linked Git worktree",
    )
    return parser.parse_args()


def main() -> int:
    try:
        return migrate(parse_args())
    except (MigrationError, OSError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
