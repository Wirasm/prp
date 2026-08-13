#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# ///
"""prp-worktree: tiny git worktree manager for parallel agent workstreams.

Worktrees live INSIDE the repo at .worktrees/<name> (excluded via
.git/info/exclude) so they stay within sandbox-writable roots on any agent
harness. Branch name == worktree name. Always operates on the main checkout,
no matter where it is run from (including from inside a worktree).

Usage:
    uv run worktree.py create <name> [--base <branch>]
    uv run worktree.py list [--base <branch>] [--json]
    uv run worktree.py remove <name> [--force] [--delete-branch]

`create` prints the worktree's absolute path as its final line so callers can
cd without parsing prose.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

WORKTREES_DIR = ".worktrees"


def die(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def git(*args: str, cwd: Path | None = None, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True
    )
    if check and result.returncode != 0:
        die(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def git_ok(*args: str, cwd: Path | None = None) -> bool:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True
    ).returncode == 0


def main_root() -> Path:
    """Root of the MAIN checkout, even when run from inside a worktree."""
    common = git("rev-parse", "--path-format=absolute", "--git-common-dir")
    return Path(common).parent


def ensure_excluded(root: Path) -> None:
    exclude = Path(git("rev-parse", "--path-format=absolute", "--git-common-dir")) / "info" / "exclude"
    pattern = f"{WORKTREES_DIR}/"
    lines = exclude.read_text().splitlines() if exclude.exists() else []
    if pattern not in lines:
        exclude.parent.mkdir(parents=True, exist_ok=True)
        exclude.write_text("\n".join([*lines, pattern]) + "\n")


def default_base(root: Path) -> str:
    head = git("symbolic-ref", "--short", "refs/remotes/origin/HEAD", cwd=root, check=False)
    if head.startswith("origin/"):
        return head
    return git("rev-parse", "--abbrev-ref", "HEAD", cwd=root)


def wt_path(root: Path, name: str) -> Path:
    return root / WORKTREES_DIR / name.replace("/", "-")


def managed_worktrees(root: Path) -> list[dict]:
    """Worktrees under .worktrees/, parsed from `git worktree list --porcelain`."""
    out = git("worktree", "list", "--porcelain", cwd=root)
    entries, current = [], {}
    for line in [*out.splitlines(), ""]:
        if not line:
            if current:
                entries.append(current)
            current = {}
        elif line.startswith("worktree "):
            current["path"] = Path(line.removeprefix("worktree "))
        elif line.startswith("branch refs/heads/"):
            current["branch"] = line.removeprefix("branch refs/heads/")
    base_dir = root / WORKTREES_DIR
    return [e for e in entries if base_dir in e["path"].parents]


def cmd_create(args: argparse.Namespace) -> None:
    root = main_root()
    base = args.base or default_base(root)
    path = wt_path(root, args.name)
    if path.exists():
        die(f"worktree already exists: {path} (remove it first, or pick another name)")
    ensure_excluded(root)
    path.parent.mkdir(exist_ok=True)
    if git_ok("show-ref", "--verify", "--quiet", f"refs/heads/{args.name}", cwd=root):
        git("worktree", "add", str(path), args.name, cwd=root)
        print(f"worktree on existing branch '{args.name}'")
    else:
        git("worktree", "add", "-b", args.name, str(path), base, cwd=root)
        print(f"worktree on new branch '{args.name}' from '{base}'")
    print(path)


def stats_for(path: Path, base: str) -> dict:
    branch = git("rev-parse", "--abbrev-ref", "HEAD", cwd=path)
    dirty = len([l for l in git("status", "--porcelain", cwd=path).splitlines() if l])
    counts = git("rev-list", "--left-right", "--count", f"{base}...HEAD", cwd=path, check=False)
    behind, ahead = (int(x) for x in counts.split()) if counts else (0, 0)
    short = git("diff", "--shortstat", f"{base}...HEAD", cwd=path, check=False)
    files = int(m.group(1)) if (m := re.search(r"(\d+) files? changed", short)) else 0
    ins = int(m.group(1)) if (m := re.search(r"(\d+) insertions?", short)) else 0
    dels = int(m.group(1)) if (m := re.search(r"(\d+) deletions?", short)) else 0
    merged = git_ok("merge-base", "--is-ancestor", "HEAD", base, cwd=path)
    last = git("log", "-1", "--format=%cr", cwd=path, check=False) or "-"
    return {
        "name": path.name, "branch": branch, "base": base,
        "ahead": ahead, "behind": behind, "dirty_files": dirty,
        "files_changed": files, "insertions": ins, "deletions": dels,
        "merged_into_base": merged, "last_commit": last, "path": str(path),
    }


def cmd_list(args: argparse.Namespace) -> None:
    root = main_root()
    base = args.base or default_base(root)
    rows = [stats_for(e["path"], base) for e in managed_worktrees(root)]
    if args.json:
        print(json.dumps(rows, indent=2))
        return
    if not rows:
        print(f"no managed worktrees under {root / WORKTREES_DIR}")
        return
    cols = ["name", "branch", "ahead", "behind", "dirty", "diff", "merged", "last commit"]
    table = [[
        r["name"], r["branch"], str(r["ahead"]), str(r["behind"]),
        str(r["dirty_files"]) if r["dirty_files"] else "-",
        f"{r['files_changed']}f +{r['insertions']}/-{r['deletions']}",
        "yes" if r["merged_into_base"] else "no", r["last_commit"],
    ] for r in rows]
    widths = [max(len(c), *(len(row[i]) for row in table)) for i, c in enumerate(cols)]
    print(f"base: {base}")
    print("  ".join(c.ljust(w) for c, w in zip(cols, widths)))
    for row in table:
        print("  ".join(v.ljust(w) for v, w in zip(row, widths)))


def cmd_remove(args: argparse.Namespace) -> None:
    root = main_root()
    path = wt_path(root, args.name)
    matches = [e for e in managed_worktrees(root) if e["path"] == path]
    if not matches:
        die(f"no managed worktree at {path} (see: worktree.py list)")
    branch = git("rev-parse", "--abbrev-ref", "HEAD", cwd=path)
    dirty = [l for l in git("status", "--porcelain", cwd=path).splitlines() if l]
    if dirty and not args.force:
        die(f"worktree has {len(dirty)} uncommitted change(s) — commit/stash them, or pass --force to discard")
    if args.delete_branch:
        base = args.base or default_base(root)
        merged = git_ok("merge-base", "--is-ancestor", branch, base, cwd=root)
        if not merged and not args.force:
            die(f"branch '{branch}' is not merged into '{base}' — kept. Merge it, or pass --force to delete anyway")
    git("worktree", "remove", *(["--force"] if args.force else []), str(path), cwd=root)
    print(f"removed worktree {path}")
    if args.delete_branch:
        # The selected-base ancestry proof (or the caller's explicit --force
        # override) is authoritative; `git branch -d` may consult a different
        # upstream, so use -D only after that gate.
        git("branch", "-D", branch, cwd=root)
        print(f"deleted branch {branch}")
    else:
        pushed = git_ok("rev-parse", "--verify", "--quiet", f"origin/{branch}", cwd=root)
        print(f"kept branch {branch} (pushed to origin: {'yes' if pushed else 'no'})")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("create", help="create .worktrees/<name> on branch <name>")
    p.add_argument("name")
    p.add_argument("--base", help="base branch for a new branch (default: origin HEAD, else current)")
    p.set_defaults(func=cmd_create)

    p = sub.add_parser("list", help="list managed worktrees with git stats")
    p.add_argument("--base", help="branch to compare against (default: origin HEAD, else current)")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("remove", help="remove a managed worktree (refuses if dirty)")
    p.add_argument("name")
    p.add_argument("--force", action="store_true", help="discard dirty state / delete unmerged branch")
    p.add_argument("--delete-branch", action="store_true", help="also delete the branch (refuses if unmerged)")
    p.add_argument("--base", help="merge-check base for --delete-branch (default: origin HEAD)")
    p.set_defaults(func=cmd_remove)

    args = ap.parse_args()
    if not git_ok("rev-parse", "--git-dir"):
        die("not inside a git repository")
    args.func(args)


if __name__ == "__main__":
    main()
